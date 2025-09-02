# Recipe Genie

AI generator web app built with Python Flask and Google Gemini.

Features:
- Login/registration required for recipe generation (SQLite-backed).
- Ask for a recipe by name or description.
- Provide ingredients you already have; the app suggests a recipe and computes a shopping list that excludes those items.
- Clean, modern UI (Bulma + some flair).

## Tech Stack
- Python (Flask)
- uv + pyproject.toml (no requirements.txt)
- Google Gemini (via `google-generativeai`)
- SQLite (via Python `sqlite3`) with hashed passwords (`werkzeug.security`)
- Bulma CSS, Font Awesome, Animate.css

## Setup

1) Install uv if you don’t have it:
   https://docs.astral.sh/uv/

2) Copy environment example and add your Gemini API key:

```bash
cp .env.example .env
# Edit .env and set GOOGLE_API_KEY
```

3) Install dependencies with uv (creates a local .venv):

```bash
uv sync
```

4) Run the app:

```bash
uv run flask --app app run --debug
# Or
uv run python app.py
```

Open http://127.0.0.1:5000

## Authentication
- Access control: `/home` and `/generate` require a logged-in session. If not authenticated, you will be redirected to `/login`.
- Register: Visit `/register` to create an account. Login at `/login`, logout at `/logout`, and use `/forgot_password` for the demo reset flow.
- Storage: Users are stored in a SQLite database at `instance/auth.db`. The database and table are created automatically on first run; no migration step is required.
- Security: Passwords are hashed using Werkzeug (no plaintext storage).

## Environment Variables
- `GOOGLE_API_KEY` (required): Your Google Gemini API key.
- `GEMINI_MODEL` (optional): Defaults to `gemini-1.5-flash`.

## Notes
- The app asks Gemini to return structured JSON for robust parsing and shopping list computation.
- Shopping list is computed by comparing the recipe’s ingredient names with your provided list (case-insensitive, basic normalization).

## Scripts
- Format: `uv run black .`
- Lint: `uv run ruff check .`

## Security
- Do not commit your `.env`. This repo ships with `.env.example` — keep secrets local.

## License
MIT (or your preferred license)

