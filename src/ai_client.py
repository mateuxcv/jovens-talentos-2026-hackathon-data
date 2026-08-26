"""Small OpenAI-compatible HTTP client used by the Streamlit application."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_ENDPOINT = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4o-mini"


class AIClientError(RuntimeError):
    """Raised when the configured LLM service cannot produce an audit."""


@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    model: str = DEFAULT_MODEL
    endpoint: str = DEFAULT_ENDPOINT
    timeout_seconds: int = 45

    @classmethod
    def from_environment(cls) -> LLMConfig | None:
        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        return cls(
            api_key=api_key,
            model=os.getenv("LLM_MODEL", DEFAULT_MODEL),
            endpoint=os.getenv("LLM_API_URL", DEFAULT_ENDPOINT),
        )


def request_analysis(
    system_prompt: str,
    user_prompt: str,
    config: LLMConfig,
) -> str:
    """Call an OpenAI-compatible chat completions endpoint directly."""

    payload = {
        "model": config.model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    request = Request(
        config.endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=config.timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise AIClientError(f"LLM API returned HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise AIClientError(f"Could not reach the configured LLM API: {exc}") from exc

    try:
        content: Any = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AIClientError("LLM API returned an unexpected response format") from exc
    if not isinstance(content, str) or not content.strip():
        raise AIClientError("LLM API returned an empty analysis")
    return content.strip()


def save_ai_log(
    system_prompt: str,
    user_prompt: str,
    response: str,
    log_dir: str | Path = "ai-log",
) -> Path:
    """Persist the complete prompt and response for delivery auditing."""

    directory = Path(log_dir)
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc)
    path = directory / f"audit-{timestamp.strftime('%Y%m%dT%H%M%SZ')}.md"
    content = (
        "# Auditoria de IA\n\n"
        f"- Gerada em: {timestamp.isoformat()}\n\n"
        "## Prompt de sistema\n\n"
        f"{system_prompt}\n\n"
        "## Evidências enviadas\n\n"
        f"{user_prompt}\n\n"
        "## Parecer\n\n"
        f"{response}\n"
    )
    path.write_text(content, encoding="utf-8")
    return path
