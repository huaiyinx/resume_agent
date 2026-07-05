"""ResumeExtractor 单元测试。

通过 mock ``LLMClient.chat`` 验证：
1. 调用参数包含 system prompt 与 raw_text。
2. 返回的 JSON 字符串被正确解析为 ``StructuredResume``。
3. 异常场景（非法 JSON、未配置 LLM）的错误处理。
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from resume_agent.llm.client import LLMClient
from resume_agent.parsers.extractor import (
    BasicInfo,
    EducationItem,
    ExperienceItem,
    ProjectItem,
    ResumeExtractor,
    StructuredResume,
)


def _make_mock_client(response_text: str) -> LLMClient:
    """构造一个 chat 方法被 mock 的 LLMClient。"""
    client = LLMClient(api_key="sk-test")
    client.chat = AsyncMock(return_value=response_text)  # type: ignore[method-assign]
    return client


def _sample_resume_json() -> dict[str, Any]:
    """构造一份样例结构化简历字典。"""
    return {
        "basic": {
            "name": "张三",
            "phone": "138****8888",
            "email": "zhangsan@example.com",
            "location": "北京",
        },
        "education": [
            {
                "school": "某大学",
                "degree": "硕士",
                "major": "计算机科学",
                "period": "2018-2021",
            }
        ],
        "experience": [
            {
                "company": "Tencent",
                "role": "安全研究员",
                "period": "2021-至今",
                "highlights": ["负责云安全", "推动漏洞体系建设"],
            }
        ],
        "projects": [
            {"name": "漏洞扫描平台", "role": "负责人", "description": "自动化扫描"}
        ],
        "skills": ["Python", "安全", "渗透测试"],
        "primary_direction": "安全",
    }


@pytest.mark.asyncio
async def test_extract_parses_valid_json() -> None:
    """LLM 返回合法 JSON 时应正确解析为 StructuredResume。"""
    sample = _sample_resume_json()
    client = _make_mock_client(json.dumps(sample, ensure_ascii=False))
    extractor = ResumeExtractor(client)

    resume = await extractor.extract("张三 简历文本 ...")

    assert isinstance(resume, StructuredResume)
    assert resume.basic.name == "张三"
    assert resume.basic.phone == "138****8888"
    assert resume.basic.email == "zhangsan@example.com"
    assert resume.basic.location == "北京"
    assert len(resume.education) == 1
    assert resume.education[0].school == "某大学"
    assert resume.education[0].degree == "硕士"
    assert len(resume.experience) == 1
    assert resume.experience[0].company == "Tencent"
    assert resume.experience[0].role == "安全研究员"
    assert resume.experience[0].highlights == ["负责云安全", "推动漏洞体系建设"]
    assert len(resume.projects) == 1
    assert resume.projects[0].name == "漏洞扫描平台"
    assert resume.skills == ["Python", "安全", "渗透测试"]
    assert resume.primary_direction == "安全"


@pytest.mark.asyncio
async def test_extract_calls_chat_with_correct_args() -> None:
    """extract 应将 system prompt 与 raw_text 传给 LLMClient.chat。"""
    client = _make_mock_client("{}")
    extractor = ResumeExtractor(client)

    await extractor.extract("raw resume text here")

    client.chat.assert_awaited_once()  # type: ignore[attr-defined]
    call_args = client.chat.call_args  # type: ignore[attr-defined]
    system_prompt = call_args.kwargs["system_prompt"]
    user_content = call_args.kwargs["user_content"]
    assert "简历解析专家" in system_prompt
    assert "primary_direction" in system_prompt
    assert "raw resume text here" in user_content
    assert call_args.kwargs["response_format_json"] is True


@pytest.mark.asyncio
async def test_extract_handles_markdown_code_block() -> None:
    """LLM 返回带 markdown 代码块的 JSON 应能剥离后解析。"""
    sample = _sample_resume_json()
    raw = f"```json\n{json.dumps(sample, ensure_ascii=False)}\n```"
    client = _make_mock_client(raw)
    extractor = ResumeExtractor(client)

    resume = await extractor.extract("text")
    assert resume.primary_direction == "安全"
    assert resume.basic.name == "张三"


@pytest.mark.asyncio
async def test_extract_handles_extra_text_around_json() -> None:
    """LLM 在 JSON 前后加解释性文字时，应能截取大括号区间解析。"""
    sample = _sample_resume_json()
    raw = f"以下是解析结果：\n{json.dumps(sample, ensure_ascii=False)}\n以上。"
    client = _make_mock_client(raw)
    extractor = ResumeExtractor(client)

    resume = await extractor.extract("text")
    assert resume.basic.name == "张三"


@pytest.mark.asyncio
async def test_extract_raises_on_invalid_json() -> None:
    """LLM 返回非 JSON 文本时抛出 RuntimeError。"""
    client = _make_mock_client("这不是 JSON")
    extractor = ResumeExtractor(client)

    with pytest.raises(RuntimeError, match="无法解析为 JSON"):
        await extractor.extract("text")


@pytest.mark.asyncio
async def test_extract_normalizes_invalid_direction() -> None:
    """primary_direction 非法时归一为「其他」。"""
    data = _sample_resume_json()
    data["primary_direction"] = "不存在的方向"
    client = _make_mock_client(json.dumps(data, ensure_ascii=False))
    extractor = ResumeExtractor(client)

    resume = await extractor.extract("text")
    assert resume.primary_direction == "其他"


@pytest.mark.asyncio
async def test_extract_defaults_when_fields_missing() -> None:
    """LLM 返回部分字段缺失时使用模型默认值。"""
    client = _make_mock_client(json.dumps({"basic": {"name": "李四"}}))
    extractor = ResumeExtractor(client)

    resume = await extractor.extract("text")
    assert resume.basic.name == "李四"
    assert resume.basic.phone is None
    assert resume.education == []
    assert resume.experience == []
    assert resume.projects == []
    assert resume.skills == []
    assert resume.primary_direction == "其他"


@pytest.mark.asyncio
async def test_extract_raises_when_llm_not_configured() -> None:
    """LLM 未配置时 extract 抛出 RuntimeError。"""
    client = LLMClient(api_key="")
    extractor = ResumeExtractor(client)

    with pytest.raises(RuntimeError, match="LLM not configured"):
        await extractor.extract("text")


@pytest.mark.asyncio
async def test_extract_raises_on_wrong_type_data() -> None:
    """LLM 返回的 JSON 顶层不是对象时抛出 RuntimeError。"""
    client = _make_mock_client('["not", "an", "object"]')
    extractor = ResumeExtractor(client)

    with pytest.raises(RuntimeError, match="不是对象"):
        await extractor.extract("text")


@pytest.mark.asyncio
async def test_extract_raises_on_malformed_basic_field() -> None:
    """basic 字段类型错误时抛出 ValidationError。"""
    data = _sample_resume_json()
    data["basic"] = "should be an object"
    client = _make_mock_client(json.dumps(data, ensure_ascii=False))
    extractor = ResumeExtractor(client)

    with pytest.raises(ValidationError):
        await extractor.extract("text")


def test_structured_resume_model_defaults() -> None:
    """StructuredResume 空构造应有合理默认值。"""
    resume = StructuredResume()
    assert isinstance(resume.basic, BasicInfo)
    assert resume.basic.name is None
    assert resume.education == []
    assert resume.experience == []
    assert resume.projects == []
    assert resume.skills == []
    assert resume.primary_direction == "其他"


def test_nested_models_independent() -> None:
    """嵌套模型类型可独立构造。"""
    basic = BasicInfo(name="test", phone="123", email="a@b.com", location="CN")
    edu = EducationItem(school="S", degree="D", major="M", period="2020")
    exp = ExperienceItem(
        company="C", role="R", period="2021", highlights=["h1", "h2"]
    )
    proj = ProjectItem(name="P", role="Lead", description="desc")
    resume = StructuredResume(
        basic=basic,
        education=[edu],
        experience=[exp],
        projects=[proj],
        skills=["Python"],
        primary_direction="后端",
    )
    assert resume.basic.name == "test"
    assert resume.education[0].school == "S"
    assert resume.experience[0].highlights == ["h1", "h2"]
    assert resume.projects[0].description == "desc"
    assert resume.primary_direction == "后端"
