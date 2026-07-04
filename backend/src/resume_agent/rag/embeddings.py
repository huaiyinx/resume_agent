"""Embedding 提供者接口骨架。

定义抽象基类 ``EmbeddingProvider`` 与具体实现占位 ``OpenAIEmbedding``。
具体调用逻辑留待 ``rag-index`` 变更完成。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from resume_agent.config import settings


class EmbeddingProvider(ABC):
    """Embedding 提供者抽象基类。

    所有具体实现（OpenAI / DeepSeek / 本地模型）需实现 ``embed_texts``。
    """

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """将文本批量转换为向量。

        Args:
            texts: 待嵌入的文本列表。

        Returns:
            与输入等长的向量列表，每个向量为浮点数列表。
        """
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        """返回向量维度。"""
        ...


class OpenAIEmbedding(EmbeddingProvider):
    """OpenAI Embedding 提供者（骨架）。

    使用 ``text-embedding-3-small`` 模型，1536 维。
    具体调用逻辑（HTTP 请求、重试、批处理）留待 ``rag-index`` 变更实现。
    """

    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        self.model = model or settings.embedding_model
        self.api_key = api_key or settings.llm_api_key

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """嵌入文本（未实现）。

        Raises:
            NotImplementedError: 具体实现留待 ``rag-index`` 变更。
        """
        raise NotImplementedError("OpenAIEmbedding.embed_texts 将在 rag-index 变更中实现")

    @property
    def dimension(self) -> int:
        """text-embedding-3-small 输出 1536 维向量。"""
        return 1536


_REGISTRY: dict[str, type[EmbeddingProvider]] = {
    "openai": OpenAIEmbedding,
}


def get_embedding_provider(provider: str | None = None) -> EmbeddingProvider:
    """按名称获取 Embedding 提供者实例。

    Args:
        provider: 提供者名称，默认使用 ``settings.embedding_provider``。

    Returns:
        Embedding 提供者实例。

    Raises:
        ValueError: 未知的提供者名称。
    """
    name = provider or settings.embedding_provider
    cls = _REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"未知的 embedding provider: {name}")
    return cls()


def available_providers() -> list[str]:
    """列出已注册的 Embedding 提供者名称。"""
    return list(_REGISTRY.keys())


def provider_info() -> dict[str, Any]:
    """返回 Embedding 配置信息，供健康检查使用。"""
    return {
        "provider": settings.embedding_provider,
        "model": settings.embedding_model,
        "configured": bool(settings.llm_api_key),
        "available": available_providers(),
    }
