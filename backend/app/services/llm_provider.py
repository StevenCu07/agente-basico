import os
from dataclasses import dataclass

import httpx

from app.services.costs import estimate_tokens_from_text


@dataclass
class LLMResult:
    text: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


def _extract_text(payload: dict) -> str:
    if isinstance(payload.get("output_text"), str) and payload["output_text"].strip():
        return payload["output_text"].strip()

    output = payload.get("output", [])
    parts: list[str] = []
    for item in output:
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                parts.append(text)
    return "\n".join(parts).strip() if parts else "No fue posible generar una respuesta."


def _mock_response(system_prompt: str, user_prompt: str) -> str:
    seed = (system_prompt + "\n" + user_prompt).strip()
    compact = " ".join(seed.split())
    if not compact:
        return "Sin contenido para procesar."
    return f"[MODO MOCK] {compact[:700]}"


def _openai_generate(system_prompt: str, user_prompt: str, max_output_tokens: int) -> LLMResult:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        text = "[FALLBACK MOCK] OPENAI_API_KEY no configurada. Respuesta simulada."
        prompt_tokens = estimate_tokens_from_text(system_prompt + user_prompt)
        completion_tokens = estimate_tokens_from_text(text)
        return LLMResult(text=text, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, total_tokens=prompt_tokens + completion_tokens)

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
        ],
        "max_output_tokens": max_output_tokens,
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPStatusError, httpx.RequestError):
        text = "[FALLBACK MOCK] No fue posible usar OpenAI en este momento. Respuesta simulada."
        prompt_tokens = estimate_tokens_from_text(system_prompt + user_prompt)
        completion_tokens = estimate_tokens_from_text(text)
        return LLMResult(text=text, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, total_tokens=prompt_tokens + completion_tokens)

    usage = data.get("usage", {})
    prompt_tokens = int(usage.get("input_tokens", estimate_tokens_from_text(system_prompt + user_prompt)))
    completion_tokens = int(usage.get("output_tokens", 0))
    text = _extract_text(data)
    if completion_tokens == 0:
        completion_tokens = estimate_tokens_from_text(text)
    return LLMResult(
        text=text,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
    )


def _gemini_generate(system_prompt: str, user_prompt: str, max_output_tokens: int) -> LLMResult:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        text = "[FALLBACK MOCK] GEMINI_API_KEY no configurada. Respuesta simulada."
        prompt_tokens = estimate_tokens_from_text(system_prompt + user_prompt)
        completion_tokens = estimate_tokens_from_text(text)
        return LLMResult(text=text, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, total_tokens=prompt_tokens + completion_tokens)

    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": f"Instrucciones del sistema:\n{system_prompt}\n\nSolicitud del usuario:\n{user_prompt}",
                    }
                ],
            }
        ],
        "generationConfig": {"maxOutputTokens": max_output_tokens},
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers={"Content-Type": "application/json"}, json=payload)
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPStatusError, httpx.RequestError):
        text = "[FALLBACK MOCK] No fue posible usar Gemini en este momento. Respuesta simulada."
        prompt_tokens = estimate_tokens_from_text(system_prompt + user_prompt)
        completion_tokens = estimate_tokens_from_text(text)
        return LLMResult(text=text, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, total_tokens=prompt_tokens + completion_tokens)

    parts = []
    for candidate in data.get("candidates", []):
        content = candidate.get("content", {})
        for part in content.get("parts", []):
            text_part = part.get("text")
            if text_part:
                parts.append(text_part)

    text = "\n".join(parts).strip() if parts else "No fue posible generar una respuesta."
    usage = data.get("usageMetadata", {})
    prompt_tokens = int(usage.get("promptTokenCount", estimate_tokens_from_text(system_prompt + user_prompt)))
    completion_tokens = int(usage.get("candidatesTokenCount", estimate_tokens_from_text(text)))
    total_tokens = int(usage.get("totalTokenCount", prompt_tokens + completion_tokens))
    return LLMResult(text=text, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, total_tokens=total_tokens)


def generate_text(system_prompt: str, user_prompt: str, max_output_tokens: int = 600) -> LLMResult:
    mode = os.getenv("LLM_MODE", "mock").lower()
    if mode == "mock":
        text = _mock_response(system_prompt, user_prompt)
        prompt_tokens = estimate_tokens_from_text(system_prompt + user_prompt)
        completion_tokens = estimate_tokens_from_text(text)
        return LLMResult(text=text, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, total_tokens=prompt_tokens + completion_tokens)
    if mode == "gemini":
        return _gemini_generate(system_prompt, user_prompt, max_output_tokens)
    return _openai_generate(system_prompt, user_prompt, max_output_tokens)
