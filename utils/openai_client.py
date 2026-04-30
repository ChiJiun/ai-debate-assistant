from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI
import requests


load_dotenv()


DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "OpenAI")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))


PROVIDER_ENV_KEYS = {
    "OpenAI": "OPENAI_API_KEY",
    "Gemini": "GEMINI_API_KEY",
    "Claude": "ANTHROPIC_API_KEY",
    "Grok": "XAI_API_KEY",
    "DeepSeek": "DEEPSEEK_API_KEY",
    "Qwen": "DASHSCOPE_API_KEY",
    "OpenRouter": "OPENROUTER_API_KEY",
}


DEFAULT_MODELS = {
    "OpenAI": "gpt-4.1-mini",
    "Gemini": "gemini-2.5-flash-lite",
    "Claude": "claude-3-5-haiku-latest",
    "Grok": "grok-4.20-reasoning",
    "DeepSeek": "deepseek-v4-flash",
    "Qwen": "qwen-plus",
    "OpenRouter": "meta-llama/llama-3.1-8b-instruct:free",
    "Ollama": "llama3.1",
}


DEFAULT_BASE_URLS = {
    "Grok": "https://api.x.ai/v1",
    "DeepSeek": "https://api.deepseek.com",
    "Qwen": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    "OpenRouter": "https://openrouter.ai/api/v1",
    "Ollama": "http://localhost:11434",
}


class OpenAIConfigError(RuntimeError):
    """Raised when LLM provider configuration is missing."""


@dataclass(frozen=True)
class LLMConfig:
    provider: str = DEFAULT_PROVIDER
    model: str = DEFAULT_MODEL
    api_key: str = ""
    base_url: str = ""


def get_default_api_key(provider: str) -> str:
    env_key = PROVIDER_ENV_KEYS.get(provider)
    if not env_key:
        return ""
    return os.getenv(env_key, "")


def _require_api_key(config: LLMConfig) -> str:
    api_key = config.api_key.strip() or get_default_api_key(config.provider)
    if not api_key:
        env_key = PROVIDER_ENV_KEYS.get(config.provider, "API key")
        raise OpenAIConfigError(f"Missing {config.provider} API key. Enter it in the sidebar or set {env_key}.")
    return api_key


def _sorted_unique(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def _normalize_gemini_model_name(name: str) -> str:
    if name.startswith("models/"):
        return name.split("/", 1)[1]
    return name


def _list_openai_models(config: LLMConfig) -> list[str]:
    client = OpenAI(api_key=_require_api_key(config))
    return _sorted_unique([model.id for model in client.models.list().data])


def _list_openai_compatible_models(config: LLMConfig) -> list[str]:
    client = OpenAI(
        api_key=_require_api_key(config),
        base_url=config.base_url or DEFAULT_BASE_URLS[config.provider],
    )
    return _sorted_unique([model.id for model in client.models.list().data])


def _list_gemini_models(config: LLMConfig) -> list[str]:
    from google import genai

    client = genai.Client(api_key=_require_api_key(config))
    models: list[str] = []
    for model in client.models.list():
        methods = getattr(model, "supported_actions", None) or getattr(model, "supported_generation_methods", None)
        if methods and "generateContent" not in methods:
            continue
        name = getattr(model, "name", "")
        models.append(_normalize_gemini_model_name(name))
    return _sorted_unique(models)


def _list_claude_models(config: LLMConfig) -> list[str]:
    import anthropic

    client = anthropic.Anthropic(api_key=_require_api_key(config))
    response = client.models.list(limit=1000)
    models = getattr(response, "data", response)
    return _sorted_unique([getattr(model, "id", "") for model in models])


def _list_openrouter_models(config: LLMConfig) -> list[str]:
    headers = {}
    api_key = config.api_key.strip() or get_default_api_key("OpenRouter")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    response = requests.get(
        f"{(config.base_url or DEFAULT_BASE_URLS['OpenRouter']).rstrip('/')}/models",
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    return _sorted_unique([model.get("id", "") for model in response.json().get("data", [])])


def _list_ollama_models(config: LLMConfig) -> list[str]:
    endpoint = (config.base_url or DEFAULT_BASE_URLS["Ollama"]).rstrip("/")
    response = requests.get(f"{endpoint}/api/tags", timeout=30)
    response.raise_for_status()
    return _sorted_unique([model.get("name", "") for model in response.json().get("models", [])])


def list_available_models(config: LLMConfig) -> list[str]:
    provider = config.provider
    if provider == "OpenAI":
        return _list_openai_models(config)
    if provider == "Gemini":
        return _list_gemini_models(config)
    if provider == "Claude":
        return _list_claude_models(config)
    if provider in {"Grok", "DeepSeek", "Qwen"}:
        return _list_openai_compatible_models(config)
    if provider == "OpenRouter":
        return _list_openrouter_models(config)
    if provider == "Ollama":
        return _list_ollama_models(config)
    raise OpenAIConfigError(f"Unsupported LLM provider: {provider}")


def _generate_openai(config: LLMConfig, prompt: str, temperature: float) -> str:
    client = OpenAI(api_key=_require_api_key(config))
    response = client.responses.create(
        model=config.model or DEFAULT_MODELS["OpenAI"],
        input=prompt,
        temperature=temperature,
    )
    return response.output_text.strip()


def _generate_openrouter(config: LLMConfig, prompt: str, temperature: float) -> str:
    return _generate_openai_chat_compatible(config, prompt, temperature)


def _generate_openai_chat_compatible(config: LLMConfig, prompt: str, temperature: float) -> str:
    client = OpenAI(
        api_key=_require_api_key(config),
        base_url=config.base_url or DEFAULT_BASE_URLS[config.provider],
    )
    response = client.chat.completions.create(
        model=config.model or DEFAULT_MODELS[config.provider],
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def _generate_grok(config: LLMConfig, prompt: str, temperature: float) -> str:
    client = OpenAI(
        api_key=_require_api_key(config),
        base_url=config.base_url or DEFAULT_BASE_URLS["Grok"],
    )
    response = client.responses.create(
        model=config.model or DEFAULT_MODELS["Grok"],
        input=prompt,
        temperature=temperature,
    )
    return response.output_text.strip()


def _generate_gemini(config: LLMConfig, prompt: str, temperature: float) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=_require_api_key(config))
    response = client.models.generate_content(
        model=config.model or DEFAULT_MODELS["Gemini"],
        contents=prompt,
        config=types.GenerateContentConfig(temperature=temperature),
    )
    return (response.text or "").strip()


def _generate_claude(config: LLMConfig, prompt: str, temperature: float) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=_require_api_key(config))
    response = client.messages.create(
        model=config.model or DEFAULT_MODELS["Claude"],
        max_tokens=4096,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return "\n".join(block.text for block in response.content if getattr(block, "type", "") == "text").strip()


def _generate_ollama(config: LLMConfig, prompt: str, temperature: float) -> str:
    endpoint = (config.base_url or DEFAULT_BASE_URLS["Ollama"]).rstrip("/")
    response = requests.post(
        f"{endpoint}/api/generate",
        json={
            "model": config.model or DEFAULT_MODELS["Ollama"],
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        },
        timeout=180,
    )
    response.raise_for_status()
    return response.json().get("response", "").strip()


def generate_text(prompt: str, *, llm_config: LLMConfig, temperature: float = 0.4) -> str:
    provider = llm_config.provider
    if provider == "OpenAI":
        return _generate_openai(llm_config, prompt, temperature)
    if provider == "Gemini":
        return _generate_gemini(llm_config, prompt, temperature)
    if provider == "Claude":
        return _generate_claude(llm_config, prompt, temperature)
    if provider == "Grok":
        return _generate_grok(llm_config, prompt, temperature)
    if provider in {"DeepSeek", "Qwen"}:
        return _generate_openai_chat_compatible(llm_config, prompt, temperature)
    if provider == "OpenRouter":
        return _generate_openrouter(llm_config, prompt, temperature)
    if provider == "Ollama":
        return _generate_ollama(llm_config, prompt, temperature)
    raise OpenAIConfigError(f"Unsupported LLM provider: {provider}")
