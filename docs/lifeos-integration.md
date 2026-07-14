# LifeOS Resume-Agent 集成

本 Fork 作为 LifeOS 职业系统的独立主引擎运行。用户仍从 Love 输入、在 LifeOS 查看；Resume-Agent 负责简历版本树、JD、Gap、导师建议和 PDF。

## 部署边界

- 生产容器加入 Nginx Proxy Manager 的外部网络 `ai-network`。NPM 继续通过容器名访问 `lifeos-resume-agent:5173`；同时只映射 `127.0.0.1:5174:5173`，供宿主机上的 LifeOS 调用，端口不会绑定到公网网卡。Resume-Agent 通过网关 `172.19.0.1:4000` 访问宿主机 LiteLLM。
- 业务 API 在配置 `INTERNAL_API_TOKEN` 后要求 `X-Resume-Agent-Token`。
- `/api/health` 保持无凭据本机探活。
- 浏览器通过 `https://chat.19991023.xyz/life/career/` 访问，由现有认证和 Nginx Proxy Manager 注入内部令牌。
- LifeOS 通过 `http://127.0.0.1:5174/api/gap-report` 调用 Gap 能力，并在服务端携带内部令牌；Love 和浏览器均不直接持有该令牌。
- 数据持久化到 `/mnt/data/life-os/resume-agent`；导入源只读挂载为 `/imports`。

香港 VPS 构建时使用固定本地镜像名 `lifeos-resume-agent:local`。必须同时传入前端子路径；否则静态资源即使返回 `200`，React Router 仍会因 `/life/career/` 未匹配而渲染空白页：

```bash
docker build --network host --build-arg VITE_BASE_PATH=/life/career/ \
  -t lifeos-resume-agent:local .
docker compose -f docker-compose.production.yml up -d --no-build resume-agent
```

## Career-Ops 冷启动

```bash
docker exec lifeos-resume-agent /app/.venv/bin/python /app/scripts/import_career_ops.py \
  --source-dir /imports/Career-Ops \
  --resume-file /imports/Career-Ops/cv.md
```

导入器以文件名幂等：知识文档已存在则跳过；`cv.md` 已上传则不重复解析。个人资料不会写入 Git 或日志。

## 香港生产状态（2026-07-14）

- 项目：`/opt/life-os-resume-agent`，分支 `agent/lifeos-integration-20260714`。
- 容器：`lifeos-resume-agent`，镜像 `lifeos-resume-agent:local`，网络 `ai-network`。
- 宿主机回环映射：`127.0.0.1:5174 -> lifeos-resume-agent:5173`，仅供同机 LifeOS 使用。
- 环境文件：`/etc/lifeos/resume-agent.env`，权限 `600`，禁止提交。
- 数据目录：`/mnt/data/life-os/resume-agent`。
- 只读导入源：`/mnt/data/life-os/resume-agent-import/Career-Ops`。
- NPM 路由：`/data/ai-project/npm/data/nginx/custom/resume-agent-location.conf`。
- NPM Token snippet：`/data/ai-project/npm/data/nginx/custom/resume-agent-token.conf`，权限 `600`。
- 初次导入：11 篇知识文档、98 个切片、1 份主简历；二次导入全部跳过。
- 旧 `career-ops` 与 `career-ops-web` 容器继续保留，尚未删除。
- `713964f` 修复工作台在 `/life/career/` 下的 React Router `basename`；生产构建还必须保留上述 `VITE_BASE_PATH` 参数。

回滚时先移除 NPM `proxy_host/2.conf` 和数据库 `advanced_config` 中的 Resume-Agent include，再执行：

```bash
cd /opt/life-os-resume-agent
docker compose -f docker-compose.production.yml down
```

## 后续链路

1. Love 在职场对话中识别 JD / HR 截图，完成视觉提取后把结构化 JD 和分析结果发送给 LifeOS 内部接口。
2. LifeOS 通过宿主机 loopback 调用 Resume-Agent 的 Gap 接口，并保存最新岗位分析和稳定去重事件。
3. LifeOS 将 Gap 摘要返回给 Love 展示，同时在职业页持久显示结果并提供全屏简历工作台入口。
