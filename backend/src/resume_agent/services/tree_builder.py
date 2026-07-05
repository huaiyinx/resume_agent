"""版本树构建服务。

根据结构化简历数据生成或更新版本树节点，实现「公司 + 方向」级别的去重。

对齐 design.md 第 2.4 节：

```
1. 确保 Master 节点存在（init_db 已 seed）
2. 查找 primary_direction 对应的 branch 节点
   - 不存在 → 创建 branch（parent_id=master, direction=primary_direction）
3. 查找同方向的 company 节点（company 字段匹配）
   - 存在 → 更新 content_json（去重，保留最新版）
   - 不存在 → 创建 company 节点（parent_id=branch_id, content_json=resume_json）
```
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from resume_agent.db.connection import get_connection
from resume_agent.parsers.extractor import StructuredResume

# 方向 → branch 显示标题映射
_DIRECTION_TITLES: dict[str, str] = {
    "安全": "安全岗方向",
    "算法": "算法岗方向",
    "后端": "后端岗方向",
    "前端": "前端岗方向",
    "数据": "数据岗方向",
    "产品": "产品岗方向",
    "其他": "其他方向",
}


class TreeBuilder:
    """根据结构化简历数据生成版本树节点。

    每次调用 ``build_from_resume`` 会：
    1. 确保 Master 节点存在；
    2. 查找或创建 primary_direction 对应的 branch 节点；
    3. 查找同方向同公司的 company 节点：存在则更新 content_json，不存在则创建。
    """

    def __init__(self, db_path: Path | str | None = None) -> None:
        """初始化 TreeBuilder。

        Args:
            db_path: 数据库路径，默认使用 ``settings.sqlite_path``。
        """
        self.db_path = db_path

    def build_from_resume(self, resume: StructuredResume) -> dict[str, Any]:
        """根据结构化简历创建或更新版本树节点。

        Args:
            resume: 已提取的结构化简历数据。

        Returns:
            包含 ``node``（创建/更新的 company 节点信息）与
            ``deduplicated``（是否命中已有 company 节点并更新）的字典。
        """
        with get_connection(self.db_path) as conn:
            self._ensure_master(conn)
            branch_node = self._find_or_create_branch(conn, resume.primary_direction)
            company_name = self._extract_company_name(resume)
            content_json = resume.model_dump_json()

            existing_company = self._find_company(
                conn, branch_node["node_id"], company_name
            )
            if existing_company is not None:
                # 命中已有 company 节点 → 更新 content_json
                self._update_company_content(
                    conn, existing_company["node_id"], content_json
                )
                node = self._fetch_node(conn, existing_company["node_id"])
                return {"node": node, "deduplicated": True}

            # 不存在 → 创建新 company 节点
            new_node = self._create_company(
                conn,
                parent_id=branch_node["node_id"],
                company=company_name,
                direction=resume.primary_direction,
                content_json=content_json,
            )
            return {"node": new_node, "deduplicated": False}

    # === 内部辅助方法 ===

    def _ensure_master(self, conn: Any) -> str:
        """确保 Master 节点存在，返回其 node_id。"""
        row: dict[str, Any] | None = conn.execute(
            "SELECT node_id FROM resume_versions WHERE node_id = ?",
            ("master",),
        ).fetchone()
        if row is not None:
            return row["node_id"]

        master_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO resume_versions (id, node_id, parent_id, node_type, title)
            VALUES (?, ?, NULL, ?, ?)
            """,
            (master_id, "master", "master", "Master 主干"),
        )
        return "master"

    def _find_or_create_branch(
        self, conn: Any, direction: str
    ) -> dict[str, Any]:
        """查找或创建 branch 节点，返回节点字典。"""
        row: dict[str, Any] | None = conn.execute(
            "SELECT * FROM resume_versions WHERE node_type = ? AND direction = ?",
            ("branch", direction),
        ).fetchone()
        if row is not None:
            return row

        title = _DIRECTION_TITLES.get(direction, f"{direction}方向")
        # 业务节点 ID 使用方向作为稳定标识（同一方向只创建一个 branch）
        node_id = f"branch-{direction}"
        node_uuid = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO resume_versions (id, node_id, parent_id, node_type, title, direction)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (node_uuid, node_id, "master", "branch", title, direction),
        )
        return {
            "id": node_uuid,
            "node_id": node_id,
            "parent_id": "master",
            "node_type": "branch",
            "title": title,
            "direction": direction,
            "content_json": None,
            "company": None,
        }

    def _find_company(
        self, conn: Any, branch_node_id: str, company_name: str
    ) -> dict[str, Any] | None:
        """查找同 branch 下同名 company 节点。"""
        if not company_name:
            return None
        row: dict[str, Any] | None = conn.execute(
            """
            SELECT * FROM resume_versions
            WHERE node_type = ? AND company = ? AND parent_id = ?
            """,
            ("company", company_name, branch_node_id),
        ).fetchone()
        return row

    def _update_company_content(
        self, conn: Any, node_id: str, content_json: str
    ) -> None:
        """更新已有 company 节点的 content_json 与 updated_at。"""
        conn.execute(
            """
            UPDATE resume_versions
            SET content_json = ?, updated_at = datetime('now')
            WHERE node_id = ?
            """,
            (content_json, node_id),
        )

    def _create_company(
        self,
        conn: Any,
        parent_id: str,
        company: str,
        direction: str,
        content_json: str,
    ) -> dict[str, Any]:
        """创建新的 company 节点并返回。"""
        node_uuid = str(uuid.uuid4())
        # 业务节点 ID：方向-公司名（去空格、小写化以保持稳定）
        safe_company = (
            company.replace(" ", "-").lower() if company else "unknown"
        )
        node_id = f"{direction}-{safe_company}"
        title = f"{company} {direction}" if company else f"{direction} 节点"

        conn.execute(
            """
            INSERT INTO resume_versions
                (id, node_id, parent_id, node_type, title, company, direction, content_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                node_uuid,
                node_id,
                parent_id,
                "company",
                title,
                company,
                direction,
                content_json,
            ),
        )
        return {
            "id": node_uuid,
            "node_id": node_id,
            "parent_id": parent_id,
            "node_type": "company",
            "title": title,
            "company": company,
            "direction": direction,
            "content_json": content_json,
        }

    def _fetch_node(self, conn: Any, node_id: str) -> dict[str, Any]:
        """查询单个节点。"""
        row: dict[str, Any] = conn.execute(
            "SELECT * FROM resume_versions WHERE node_id = ?",
            (node_id,),
        ).fetchone()
        return row

    def _extract_company_name(self, resume: StructuredResume) -> str:
        """从结构化简历中提取代表公司名。

        优先取第一条 experience 的 company；否则取第一条 projects 的 name 兜底。
        """
        if resume.experience:
            company = resume.experience[0].company
            if company:
                return company
        if resume.projects:
            name = resume.projects[0].name
            if name:
                return name
        return "Unknown"


__all__ = ["TreeBuilder"]
