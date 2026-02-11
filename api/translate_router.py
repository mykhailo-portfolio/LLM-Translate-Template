"""
Template: POST /api/translate — accepts JSON, calls LLM module, returns translations.

Router naming (for portfolio / integration): this module defines the path "/translate"
only. The full URL is determined by how you mount the router. Typical usage:
    app.include_router(translate_router, prefix="/api", tags=["translate"])
→ full path becomes /api/translate. The frontend uses API_TRANSLATE = "/api/translate"
to match this. If you mount under another prefix (e.g. prefix="/v1"), set the
frontend base URL accordingly (e.g. "/v1/translate") or document it for the client.

Production recommendations (not implemented in this template):
- Require valid session (e.g. Depends(get_session_payload)) and return 401 if missing.
- Require CSRF token for POST; validate and return 403 on failure.
- Apply rate limiting (e.g. per user/session/IP) to prevent abuse.
- Check permissions (e.g. is_admin or scope) before allowing translate.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Import from template llm module (adjust path when copying into your repo)
# from llm.translate import translate
# For this template we use a relative sibling package; in your project use your package path.
try:
    from llm.translate import translate
except ImportError:
    # Placeholder when llm is not installed as package
    async def translate(text: str, source_lang: str, target_langs: list[str]) -> dict[str, str]:
        return {lang: f"[translate not wired: {text[:20]}...]" for lang in target_langs}

logger = logging.getLogger(__name__)

router = APIRouter()


class TranslateRequest(BaseModel):
    """Request body for POST /api/translate."""

    source_lang: str = Field(default="en", description="Source language code")
    target_langs: list[str] = Field(default_factory=list, description="Target language codes")
    text: str = Field(default="", description="Text to translate")


@router.post("/translate")
async def api_translate(body: TranslateRequest) -> dict[str, str]:
    """
    Translate text from source_lang to target_langs via LLM.
    Request JSON: { "source_lang": str, "target_langs": list[str], "text": str }.
    Response: { "<lang>": "<translated text>", ... }.
    """
    source_lang = (body.source_lang or "en").strip()
    text = (body.text or "").strip()
    target_langs = [str(l).strip() for l in (body.target_langs or []) if str(l).strip()]

    if not text:
        raise HTTPException(status_code=400, detail="Missing or empty text")
    if not target_langs:
        raise HTTPException(status_code=400, detail="At least one target language required")

    try:
        result = await translate(text=text, source_lang=source_lang, target_langs=target_langs)
        # Optional XSS: before returning, run each value through your sanitize/escape
        # (see LLM-Translate-Template/xss/README.md). Example: result = {k: sanitize(v) for k, v in result.items()}
        return result
    except Exception as e:
        logger.exception("Translation failed: %s", e)
        raise HTTPException(status_code=500, detail="Translation failed")
