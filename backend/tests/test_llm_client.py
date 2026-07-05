"""LLMClient 单元测试。

通过 mock ``AsyncOpenAI`` 验证 chat 方法的调用参数与返回值，
不发送任何真实 HTTP 请求。
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from resume_agent.llm.client import LLMClient, get_default_client


def _build_mock_response(text: str) -> MagicMock:
    """构造一个模拟的 OpenAI chat completion 响应对象。"""
    response = MagicMock()
    message = MagicMock()
    message.content = text
    choice = MagicMock()
    choice.message = message
    response.choices = [choice]
    return response


def test_init_defaults_from_settings() -> None:
    """未传参时从 settings 读取默认配置。"""
    client = LLMClient()
    # settings 在 conftest 中被隔离，llm_api_key 默认为空字符串
    assert client.api_key == settings_value("llm_api_key")
    assert client.model == "gpt-4o"


def settings_value(name: str) -> Any:
    """读取当前 settings 单例字段（隔离后的）。"""
    from resume_agent.config import settings

    return getattr(settings, name)


def test_init_with_explicit_args() -> None:
    """显式传参覆盖 settings。"""
    client = LLMClient(
        provider="deepseek",
        api_key="sk-test-key",
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
    )
    assert client.provider == "deepseek"
    assert client.api_key == "sk-test-key"
    assert client.base_url == "https://api.deepseek.com"
    assert client.model == "deepseek-chat"
    assert client.configured is True


def test_configured_false_when_no_key() -> None:
    """api_key 为空时 configured 为 False。"""
    client = LLMClient(api_key="")
    assert client.configured is False


def test_build_client_passes_base_url() -> None:
    """base_url 非空时传递给 AsyncOpenAI。"""
    client = LLMClient(api_key="sk-test", base_url="https://api.deepseek.com")
    with patch("resume_agent.llm.client.AsyncOpenAI") as mock_openai_cls:
        client._build_client()
    mock_openai_cls.assert_called_once_with(
        api_key="sk-test",
        base_url="https://api.deepseek.com",
    )


def test_build_client_omits_empty_base_url() -> None:
    """base_url 为空时不应传递给 AsyncOpenAI。"""
    client = LLMClient(api_key="sk-test", base_url="")
    with patch("resume_agent.llm.client.AsyncOpenAI") as mock_openai_cls:
        client._build_client()
    mock_openai_cls.assert_called_once_with(api_key="sk-test")


@pytest.mark.asyncio
async def test_chat_raises_when_not_configured() -> None:
    """api_key 为空时 chat 方法抛出 RuntimeError。"""
    client = LLMClient(api_key="")
    with pytest.raises(RuntimeError, match="LLM not configured"):
        await client.chat("system", "user")


@pytest.mark.asyncio
async def test_chat_returns_assistant_content() -> None:
    """chat 方法返回助手消息文本。"""
    client = LLMClient(api_key="sk-test", model="gpt-4o-mini")
    mock_response = _build_mock_response("hello world")

    mock_instance = MagicMock()
    mock_instance.chat = MagicMock()
    mock_instance.chat.completions = MagicMock()
    mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("resume_agent.llm.client.AsyncOpenAI", return_value=mock_instance):
        result = await client.chat("sys prompt", "user content")

    assert result == "hello world"
    mock_instance.chat.completions.create.assert_awaited_once()
    call_kwargs = mock_instance.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"
    assert call_kwargs["messages"] == [
        {"role": "system", "content": "sys prompt"},
        {"role": "user", "content": "user content"},
    ]
    # 默认不要求 JSON 格式
    assert "response_format" not in call_kwargs


@pytest.mark.asyncio
async def test_chat_with_response_format_json() -> None:
    """response_format_json=True 时传递 response_format 参数。"""
    client = LLMClient(api_key="sk-test")
    mock_response = _build_mock_response('{"key": "value"}')

    mock_instance = MagicMock()
    mock_instance.chat = MagicMock()
    mock_instance.chat.completions = MagicMock()
    mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("resume_agent.llm.client.AsyncOpenAI", return_value=mock_instance):
        result = await client.chat("sys", "user", response_format_json=True)

    assert result == '{"key": "value"}'
    call_kwargs = mock_instance.chat.completions.create.call_args.kwargs
    assert call_kwargs["response_format"] == {"type": "json_object"}


@pytest.mark.asyncio
async def test_chat_handles_none_content() -> None:
    """助手消息 content 为 None 时返回空字符串。"""
    client = LLMClient(api_key="sk-test")
    response = MagicMock()
    message = MagicMock()
    message.content = None
    choice = MagicMock()
    choice.message = message
    response.choices = [choice]

    mock_instance = MagicMock()
    mock_instance.chat.completions.create = AsyncMock(return_value=response)

    with patch("resume_agent.llm.client.AsyncOpenAI", return_value=mock_instance):
        result = await client.chat("sys", "user")

    assert result == ""


def test_get_default_client() -> None:
    """get_default_client 构造基于 settings 的实例。"""
    client = get_default_client()
    assert isinstance(client, LLMClient)
    assert client.api_key == settings_value("llm_api_key")
