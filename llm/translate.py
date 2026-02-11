"""
LLM translate: one function translate(text, source_lang, target_langs) -> dict[lang, text].
Pseudo-prompt: "translate to these languages, return JSON". Adapters: OpenAI, Anthropic.
No e-commerce, no ban_words; minimal and generic. Optional: add content-policy logic in production.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

# Provider selection: set env e.g. LLM_TRANSLATE_PROVIDER=openai or anthropic
TRANSLATE_PROVIDER = os.environ.get("LLM_TRANSLATE_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

OPENAI_MODEL = os.environ.get("LLM_OPENAI_MODEL", "gpt-4o-mini")
ANTHROPIC_MODEL = os.environ.get("LLM_ANTHROPIC_MODEL", "claude-sonnet-4")

# Minimal universal prompt; no domain logic (e-commerce/ban_words etc.).
# For production you may add: prohibited content rules, max length, output format constraints.
SYSTEM_PROMPT = """You are a translator. Translate the given text from the source language to each target language.
Return ONLY a JSON object: keys = language codes (e.g. "ru", "uk"), values = translated text as strings.
No markdown, no explanation. Example: {"ru": "переведённый текст", "uk": "перекладений текст"}."""


def _build_user_message(text: str, source_lang: str, target_langs: list[str]) -> str:
    payload = {
        "source_lang": source_lang,
        "target_langs": target_langs,
        "text": text,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _extract_json_from_text(content: str) -> str:
    content = content.strip()
    if content.startswith("```"):
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end > start:
            content = content[start:end]
    return content


def _parse_result(raw: str, target_langs: list[str]) -> dict[str, str]:
    """Parse LLM response into dict[lang, text]. Only include target_langs."""
    out: dict[str, str] = {}
    try:
        raw = _extract_json_from_text(raw)
        data = json.loads(raw)
        if not isinstance(data, dict):
            return {lang: "" for lang in target_langs}
        for lang in target_langs:
            val = data.get(lang)
            out[lang] = str(val).strip() if val is not None else ""
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning("Failed to parse LLM response as JSON: %s", e)
        out = {lang: "" for lang in target_langs}
    return out


async def translate(
    text: str,
    source_lang: str,
    target_langs: list[str],
) -> dict[str, str]:
    """
    Translate text from source_lang to each language in target_langs using an LLM.
    Returns dict mapping language code -> translated text.
    """
    target_langs = [str(l).strip() for l in target_langs if str(l).strip()]
    if not target_langs:
        return {}

    user_message = _build_user_message(text, source_lang, target_langs)

    if TRANSLATE_PROVIDER == "anthropic":
        return await _translate_anthropic(user_message, target_langs)
    return await _translate_openai(user_message, target_langs)


async def _translate_openai(user_message: str, target_langs: list[str]) -> dict[str, str]:
    """OpenAI adapter."""
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set; returning empty translations")
        return {lang: "" for lang in target_langs}

    try:
        from openai import AsyncOpenAI
    except ImportError:
        logger.error("openai package not installed")
        return {lang: "" for lang in target_langs}

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model=OPENAI_MODEL,
        max_completion_tokens=2048,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
    )

    content = ""
    if response.choices and response.choices[0].message.content:
        content = response.choices[0].message.content
    return _parse_result(content, target_langs)


async def _translate_anthropic(user_message: str, target_langs: list[str]) -> dict[str, str]:
    """Anthropic adapter."""
    if not ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set; returning empty translations")
        return {lang: "" for lang in target_langs}

    try:
        from anthropic import AsyncAnthropic
    except ImportError:
        logger.error("anthropic package not installed")
        return {lang: "" for lang in target_langs}

    client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    response = await client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    content = ""
    if response.content and len(response.content) > 0:
        first = response.content[0]
        if hasattr(first, "text"):
            content = first.text
        elif isinstance(first, dict):
            content = first.get("text", "")
        else:
            content = str(first)
    return _parse_result(content, target_langs)
