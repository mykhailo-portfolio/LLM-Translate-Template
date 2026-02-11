/**
 * Request: builds payload, POST to /api/translate, handles response and displays result.
 * For N fields: build payload with array of { field_id, text } and map response
 * back to fields by field_id (or use one result area with lang-keyed output).
 *
 * URL note: full path is /api/translate because the API router is mounted with
 * prefix="/api" (see api/translate_router.py docstring). If your app uses another
 * prefix, set API_TRANSLATE accordingly (e.g. "/v1/translate").
 */

const sourceLangSelect = document.getElementById("source-lang");
const targetLangsInput = document.getElementById("target-langs");
const sourceTextField = document.getElementById("source-text");
const translateBtn = document.getElementById("translate-btn");
const resultArea = document.getElementById("result-area");
const resultContent = document.getElementById("result-content");

/** Full path to translate endpoint; must match router mount prefix (e.g. prefix="/api" → "/api/translate"). */
const API_TRANSLATE = "/api/translate";

async function doTranslate() {
  if (!sourceTextField || !translateBtn) return;

  const source_lang = sourceLangSelect?.value?.trim() || "en";
  const target_langs_raw = targetLangsInput?.value?.trim() || "";
  const target_langs = target_langs_raw ? target_langs_raw.split(",").map((s) => s.trim()).filter(Boolean) : [];
  const text = sourceTextField.value.trim();

  if (!text) return;
  if (target_langs.length === 0) {
    resultArea.hidden = false;
    resultContent.textContent = "Error: specify at least one target language (e.g. ru,uk).";
    return;
  }

  translateBtn.disabled = true;
  translateBtn.textContent = "Translating…";

  try {
    const response = await fetch(API_TRANSLATE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source_lang, target_langs, text }),
      // credentials: "include" if using session cookies in production
    });

    const data = await response.json().catch(() => ({}));

    resultArea.hidden = false;
    if (!response.ok) {
      resultContent.textContent = `Error ${response.status}: ${data.detail || response.statusText || "Unknown error"}`;
      return;
    }

    // Response shape: { "ru": "привет", "uk": "привіт", "en": "hello" ... }
    resultContent.textContent = JSON.stringify(data, null, 2);
    // To fill separate fields per language: for (const [lang, value] of Object.entries(data)) { document.getElementById(`out-${lang}`).value = value; }
  } finally {
    translateBtn.disabled = false;
    translateBtn.textContent = "Translate";
  }
}

if (translateBtn) {
  translateBtn.addEventListener("click", doTranslate);
}

export { doTranslate };
