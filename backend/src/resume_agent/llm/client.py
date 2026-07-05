"""统一 LLM 客户端实现。

基于 ``openai`` Python SDK 的 ``AsyncOpenAI``，通过 ``base_url`` 参数支持
OpenAI / DeepSeek / Moonshot / 本地 Ollama / Anthropic OpenAI-compatible 端点等
多提供商。一个 SDK 覆盖所有兼容 OpenAI 协议的服务，减少依赖。

对齐 design.md 第 2.1 节。
"""

from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI

from resume_agent.config import settings


class LLMClient:
    """统一 LLM 客户端，支持 OpenAI / DeepSeek / 自定义端点。

    通过 ``openai`` SDK 的 ``base_url`` 参数适配不同提供商：
    - OpenAI 官方：默认 ``https://api.openai.com/v1``，无需设置 base_url
    - DeepSeek：``https://api.deepseek.com``
    - Moonshot：``https://api.moonshot.cn/v1``
    - 本地 Ollama：``http://localhost:11434/v1``
    - Anthropic 兼容端点：参考官方文档

    Attributes:
        provider: 提供商标识（openai / deepseek / custom 等）。
        api_key: API Key，为空表示未配置。
        base_url: 自定义端点 URL，空字符串表示使用 SDK 默认。
        model: 默认模型名。
    """

    def __init__(
        self,
        provider: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        """初始化 LLM 客户端。

        Args:
            provider: 提供商标识，默认取 ``settings.llm_provider``。
            api_key: API Key，默认取 ``settings.llm_api_key``。
            base_url: 自定义端点 URL，默认取 ``settings.llm_base_url``。
            model: 默认模型名，默认 ``gpt-4o``。
        """
        self.provider: str = provider if provider is not None else settings.llm_provider
        self.api_key: str = api_key if api_key is not None else settings.llm_api_key
        self.base_url: str = base_url if base_url is not None else settings.llm_base_url
        self.model: str = model or settings.llm_model

    @property
    def configured(self) -> bool:
        """是否已配置 API Key。"""
        return bool(self.api_key)

    def _build_client(self) -> AsyncOpenAI:
        """构造 ``AsyncOpenAI`` 实例。

        ``base_url`` 为空字符串时不传递，使用 SDK 默认值。
        """
        kwargs: dict[str, Any] = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return AsyncOpenAI(**kwargs)

    async def chat(
        self,
        system_prompt: str,
        user_content: str,
        response_format_json: bool = False,
    ) -> str:
        """发送 chat completion 请求并返回助手消息文本。

        Args:
            system_prompt: system 角色提示词。
            user_content: user 角色消息内容。
            response_format_json: 是否要求模型返回 JSON 对象
                （``response_format={"type": "json_object"}``）。

        Returns:
            助手消息的文本内容。

        Raises:
            RuntimeError: ``api_key`` 为空时抛出 ``"LLM not configured"``。
        """
        if not self.api_key:
            raise RuntimeError("LLM not configured")

        client = self._build_client()
        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        if response_format_json:
            kwargs["response_format"] = {"type": "json_object"}

        response = await client.chat.completions.create(**kwargs)
        # openai SDK 返回的 choice.message.content 可能为 None，做兜底
        content = response.choices[0].message.content
        return content if content is not None else ""


def get_default_client() -> LLMClient:
    """构造基于 ``settings`` 的默认 LLM 客户端实例。"""
    return LLMClient()


__all__ = ["LLMClient", "get_default_client"]
