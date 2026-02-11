# LLM Translate – template

Full-chain template: one source field → JS → API → LLM → translations. Each part is a separate, pluggable file. No bot, no tokens, no permission checks in the template; optional XSS block included.

## Structure

```
LLM-Translate-Template/
├── .env.example            # Env vars for LLM (OPENAI_API_KEY, ANTHROPIC_API_KEY, LLM_TRANSLATE_PROVIDER, etc.)
├── README.md
├── requirements.txt        # fastapi, pydantic, openai, anthropic
├── frontend/
│   ├── index.html          # One textarea, optional lang selects, Translate button
│   └── js/
│       ├── listener.js     # Enables/disables button from source field
│       └── request.js     # POST /api/translate, display result
├── api/
│   └── translate_router.py # POST /api/translate; mount in your FastAPI app
├── llm/
│   ├── __init__.py
│   └── translate.py       # translate(text, source_lang, target_langs) → dict[lang, text]; OpenAI + Anthropic
└── xss/
    ├── README.md           # Where and how to plug sanitization
    └── placeholder.txt    # Hook points, no library chosen
```

## Frontend

- **HTML:** Single source field; comment in file explains extending to N fields (same scheme, extra blocks or loop).
- **listener.js:** Listens to input, toggles Translate button; no domain logic.
- **request.js:** Builds `{ source_lang, target_langs, text }`, POST to `/api/translate`, shows JSON result (or fill per-lang fields; see comment in file).

## API

- **POST /api/translate**  
  Body: `{ "source_lang": "en", "target_langs": ["ru", "uk"], "text": "Hello" }`  
  Response: `{ "ru": "…", "uk": "…" }`  
  In code: session, CSRF, rate limit, and permission checks are **not** implemented; comments in `translate_router.py` note that they are recommended for production.

## LLM

- **translate(text, source_lang, target_langs)** in `llm/translate.py`.  
  Uses a minimal prompt (“translate to these languages, return JSON”).  
  Adapters: OpenAI and Anthropic; provider via env `LLM_TRANSLATE_PROVIDER=openai|anthropic`.  
  Env: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`; optional `LLM_OPENAI_MODEL`, `LLM_ANTHROPIC_MODEL`.  
  No e-commerce or ban_words logic; add in your project if needed.

## XSS

- **xss/README.md:** Where to plug sanitization/escaping (output vs input) and placeholder hook points.  
- **xss/placeholder.txt:** Reminder to integrate your own library (no concrete lib in template).

## Using in your repo

1. Copy `LLM-Translate-Template/` (or its parts) into your project.
2. Ensure `llm` is importable from where the API runs (e.g. add template root to `PYTHONPATH` or move `llm` into your app package). Fix the import in `api/translate_router.py` if needed.
3. Mount the router: `app.include_router(translate_router, prefix="/api", tags=["translate"])`. The full path is then `/api/translate`; the frontend’s `API_TRANSLATE` in `request.js` must match (see docstring in `api/translate_router.py`).
4. Serve `frontend/` (e.g. static or your existing pages) and set the script’s `API_TRANSLATE` to your base URL if you use another prefix.
5. Copy `.env.example` to `.env` and set env for the chosen provider (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`, and `LLM_TRANSLATE_PROVIDER`).
6. For production: add session, CSRF, rate limit; optionally sanitize translation output before return (comment in `api/translate_router.py` and `xss/README.md`).
