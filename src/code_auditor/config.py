from __future__ import annotations

import os

from langchain_openai import ChatOpenAI


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def create_llm(temperature: float = 0.0) -> ChatOpenAI:
    """Создать LLM-клиент для OpenAI-compatible endpoint (например, vLLM)."""
    return ChatOpenAI(
        model=get_env("MODEL_NAME", "qwen3-32b"),
        base_url=get_env("LITELLM_BASE_URL", ""),
        api_key=get_env("LITELLM_API_KEY", ""),
        temperature=temperature,
    )
