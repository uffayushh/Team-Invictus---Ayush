
import json
import logging
import time
from typing import TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from app.core.config import settings

logger = logging.getLogger("llm_client")

T = TypeVar("T", bound=BaseModel)

MAX_RETRIES = 2
REQUEST_TIMEOUT = 30


class LLMCallError(Exception):
    pass


def _provider() -> str:
    return getattr(settings, "LLM_PROVIDER", "gemini").lower()


def call_llm(prompt: str, system: str | None = None, temperature: float = 0.2) -> str:
    """Plain text completion. Returns the model's raw text response."""
    provider = _provider()
    last_error = None

    for attempt in range(1, MAX_RETRIES + 2):
        try:
            start = time.monotonic()
            if provider == "groq":
                text = _call_groq(prompt, system, temperature)
            else:
                text = _call_gemini(prompt, system, temperature)
            elapsed = time.monotonic() - start
            logger.info("llm_call provider=%s attempt=%d elapsed=%.2fs", provider, attempt, elapsed)
            return text
        except Exception as e:
            last_error = e
            logger.warning("llm_call failed attempt=%d/%d error=%s", attempt, MAX_RETRIES + 1, e)

    raise LLMCallError(f"LLM call failed after {MAX_RETRIES + 1} attempts: {last_error}")


def call_llm_json(prompt: str, schema: type[T], system: str | None = None, temperature: float = 0.1) -> T:
    
    json_instruction = (
        f"\n\nRespond with ONLY valid JSON matching this schema, no preamble, "
        f"no markdown code fences:\n{schema.model_json_schema()}"
    )
    full_prompt = prompt + json_instruction
    last_error = None

    for attempt in range(1, MAX_RETRIES + 2):
        try:
            raw = call_llm(full_prompt, system=system, temperature=temperature)
            cleaned = _strip_code_fences(raw)
            data = json.loads(cleaned)
            return schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            logger.warning("llm_call_json malformed output attempt=%d error=%s", attempt, e)
            full_prompt = (
                prompt + json_instruction +
                f"\n\nYour previous response was invalid: {e}\nReturn ONLY corrected valid JSON."
            )
        except LLMCallError as e:
            last_error = e
            break

    raise LLMCallError(f"LLM JSON call failed after retries: {last_error}")


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return text.strip()


def _call_gemini(prompt: str, system: str | None, temperature: float) -> str:
    api_key = settings.GEMINI_API_KEY
    model = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    contents = []
    if system:
        contents.append({"role": "user", "parts": [{"text": system}]})
        contents.append({"role": "model", "parts": [{"text": "Understood."}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    resp = httpx.post(
        url,
        json={"contents": contents, "generationConfig": {"temperature": temperature}},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _call_groq(prompt: str, system: str | None, temperature: float) -> str:
    api_key = settings.GROQ_API_KEY
    model = getattr(settings, "GROQ_MODEL", "llama-3.1-8b-instant")
    url = "https://api.groq.com/openai/v1/chat/completions"

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = httpx.post(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": model, "messages": messages, "temperature": temperature},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]