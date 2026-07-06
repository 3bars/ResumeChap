"""ai-engine: optional, pluggable AI provider layer.

The AI features (currently: summarizing differences between two resume
versions) are entirely optional. If disabled, the app still works fully and
falls back to a plain textual diff.

Supported providers:
  - abacus     : uses the pre-configured Abacus.AI environment (no key needed)
  - openai     : OpenAI Chat Completions API
  - anthropic  : Anthropic Messages API
  - gemini     : Google Gemini API
  - copilot    : Azure OpenAI / Microsoft Copilot-style endpoint

Settings (including API keys) are persisted to a JSON file in the per-user
data directory. Keys are never committed to the repository.
"""
import difflib
import json
from pathlib import Path
from typing import List, Optional

import httpx

from database import DATA_DIR

SETTINGS_PATH = DATA_DIR / "ai_settings.json"

AVAILABLE_PROVIDERS = ["abacus", "openai", "anthropic", "gemini", "copilot"]

DEFAULT_MODELS = {
    "abacus": "route-llm",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-sonnet-20241022",
    "gemini": "gemini-1.5-flash",
    "copilot": "gpt-4o",
}

_SYSTEM_PROMPT = (
    "You are an expert resume reviewer. Compare two versions of the same "
    "resume and produce a concise, well-structured summary of what changed "
    "between them. Focus on substantive differences: added or removed "
    "experience, changed skills/keywords, tone, emphasis, and how the "
    "changes shift the resume's positioning for different roles. Use short "
    "bullet points grouped under clear headings. Be specific and practical."
)


# ---------- Settings persistence ----------
def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        try:
            return json.loads(SETTINGS_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"enabled": False, "provider": "abacus", "model": None, "api_key": None, "endpoint": None}


def save_settings(settings: dict) -> dict:
    current = load_settings()
    current.update({k: v for k, v in settings.items() if v is not None or k == "enabled"})
    SETTINGS_PATH.write_text(json.dumps(current, indent=2))
    return current


def settings_public_view(settings: dict) -> dict:
    """Settings without leaking the API key value."""
    return {
        "enabled": bool(settings.get("enabled")),
        "provider": settings.get("provider") or "abacus",
        "model": settings.get("model"),
        "endpoint": settings.get("endpoint"),
        "has_api_key": bool(settings.get("api_key")),
        "available_providers": AVAILABLE_PROVIDERS,
    }


# ---------- Text diff (always available) ----------
def build_text_diff(text_a: str, text_b: str, label_a: str, label_b: str) -> str:
    diff = difflib.unified_diff(
        text_a.splitlines(),
        text_b.splitlines(),
        fromfile=label_a,
        tofile=label_b,
        lineterm="",
    )
    return "\n".join(diff) or "(No textual differences found.)"


# ---------- Provider calls ----------
class AIError(Exception):
    pass


def _messages(text_a: str, text_b: str, label_a: str, label_b: str) -> str:
    return (
        f"### Version A — {label_a}\n{text_a}\n\n"
        f"### Version B — {label_b}\n{text_b}\n\n"
        "Summarize the differences from Version A to Version B."
    )


def _call_abacus(model: Optional[str], user_prompt: str) -> str:
    import abacusai

    client = abacusai.ApiClient()
    result = client.evaluate_prompt(
        prompt=user_prompt,
        system_message=_SYSTEM_PROMPT,
        llm_name=model if model and model != "route-llm" else None,
    )
    return getattr(result, "content", None) or str(result)


def _call_openai(model: str, api_key: str, user_prompt: str) -> str:
    resp = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_anthropic(model: str, api_key: str, user_prompt: str) -> str:
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 1024,
            "system": _SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_prompt}],
        },
        timeout=60,
    )
    resp.raise_for_status()
    return "".join(block.get("text", "") for block in resp.json().get("content", []))


def _call_gemini(model: str, api_key: str, user_prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    resp = httpx.post(
        url,
        json={
            "system_instruction": {"parts": [{"text": _SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
        },
        timeout=60,
    )
    resp.raise_for_status()
    candidates = resp.json().get("candidates", [])
    if not candidates:
        raise AIError("Gemini returned no candidates.")
    return "".join(p.get("text", "") for p in candidates[0]["content"]["parts"])


def _call_copilot(model: str, api_key: str, endpoint: str, user_prompt: str) -> str:
    if not endpoint:
        raise AIError("Copilot/Azure OpenAI requires an 'endpoint' to be configured.")
    url = f"{endpoint.rstrip('/')}/openai/deployments/{model}/chat/completions?api-version=2024-02-01"
    resp = httpx.post(
        url,
        headers={"api-key": api_key},
        json={
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def summarize_diff(text_a: str, text_b: str, label_a: str, label_b: str) -> str:
    """Generate an AI summary of the diff. Raises AIError on failure."""
    settings = load_settings()
    if not settings.get("enabled"):
        raise AIError("AI engine is disabled.")

    provider = (settings.get("provider") or "abacus").lower()
    model = settings.get("model") or DEFAULT_MODELS.get(provider)
    api_key = settings.get("api_key")
    endpoint = settings.get("endpoint")
    user_prompt = _messages(text_a, text_b, label_a, label_b)

    try:
        if provider == "abacus":
            return _call_abacus(model, user_prompt)
        if provider in {"openai", "anthropic", "gemini", "copilot"} and not api_key:
            raise AIError(f"Provider '{provider}' requires an API key.")
        if provider == "openai":
            return _call_openai(model, api_key, user_prompt)
        if provider == "anthropic":
            return _call_anthropic(model, api_key, user_prompt)
        if provider == "gemini":
            return _call_gemini(model, api_key, user_prompt)
        if provider == "copilot":
            return _call_copilot(model, api_key, endpoint, user_prompt)
        raise AIError(f"Unknown provider: {provider}")
    except httpx.HTTPStatusError as exc:
        raise AIError(f"{provider} API error: {exc.response.status_code} {exc.response.text[:200]}") from exc
    except Exception as exc:  # noqa: BLE001 - surface a clean message to the UI
        raise AIError(f"{provider} request failed: {exc}") from exc
