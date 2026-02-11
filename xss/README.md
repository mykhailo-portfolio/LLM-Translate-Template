# XSS protection for LLM translate output

This block describes **where** and **how** to plug sanitization/escaping for translated text. No specific library is chosen here — use whatever fits your stack (e.g. DOMPurify, a server-side escaping library, or framework-built-in escaping).

## Where to apply

1. **On output (recommended)**  
   When you render the translation in HTML (e.g. into a `<div>`, form field, or table cell), escape or sanitize **before** inserting into the DOM or template:
   - **Server-side:** escape in your template engine (Jinja2 `{{ value | e }}`, React default escaping, etc.) or with a dedicated HTML-escaping function.
   - **Client-side:** if you set `innerHTML` or use raw HTML, use a sanitizer (e.g. DOMPurify) on the string; otherwise prefer `textContent` or safe template APIs so that no HTML is interpreted.

2. **On input (optional)**  
   You may also normalize or strip dangerous content from the **source** text before sending to the API (e.g. strip `<script>` tags). This reduces risk if the same text is later shown elsewhere; it does not replace output escaping.

## Placeholder

- **Backend (API):** before returning the response, you can run each translated string through an escape/sanitize function and return the safe string. Example (pseudo): `return { lang: sanitize_or_escape(translated) for lang, translated in result.items() }`.
- **Frontend (JS):** before writing to the page, e.g. `element.textContent = translated` (safe) or `element.innerHTML = yourSanitizer(translated)` (if you need limited HTML and use a sanitizer).

Do **not** trust the LLM output as safe HTML; always treat it as untrusted and escape or sanitize at the point of use.
