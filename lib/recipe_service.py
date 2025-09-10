import os
import json
import re
from typing import Dict, Any, List, Tuple

# Google Gemini (configured in app.py). Import lazily/fallback for test environments without the package.
try:
    import google.generativeai as genai  # type: ignore
except (
    Exception
):  # pragma: no cover - fallback for environments without google-generativeai

    class _GenAIStub:
        class GenerativeModel:
            def __init__(self, *args, **kwargs):
                # This will be monkeypatched in tests; if used directly, raise to signal misconfiguration.
                raise RuntimeError(
                    "google-generativeai is not installed; configure genai in app or monkeypatch in tests"
                )

    genai = _GenAIStub()  # type: ignore


def get_model():
    """Configure and return a Gemini model instance.
    Note: genai.configure(api_key=...) is expected to be called by the app on startup.
    """
    return genai.GenerativeModel(
        model_name=os.environ.get("GEMINI_MODEL", "gemini-1.5-flash"),
        system_instruction=(
            "You are Recipe Genie, a helpful culinary assistant. Always produce"
            " well-structured recipes as valid JSON strictly following the schema."
        ),
    )


def normalize_name(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[()\[\]{}]", " ", s)
    s = re.sub(r"[^a-z0-9\s\-]", "", s)
    s = re.sub(r"\s+", " ", s)
    # Simple plural trim: remove a single trailing 's' for basic normalization
    if s.endswith("s") and len(s) > 2:
        s = s[:-1]
    return s.strip()


def parse_available_ingredients(raw: str) -> List[str]:
    if not raw:
        return []
    parts = re.split(r"[\n,]", raw)
    result = []
    for p in parts:
        normalized = normalize_name(p)
        if normalized and isinstance(normalized, str):
            result.append(normalized)
    return result


def diff_shopping_list(
    recipe_ingredients: List[Dict[str, Any]],
    available: List[str],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Return (shopping_list, have_list). Match by normalized ingredient name containment."""
    have = set(str(item) for item in available if item)
    shopping: List[Dict[str, Any]] = []
    have_items: List[Dict[str, Any]] = []

    for item in recipe_ingredients:
        name = normalize_name(item.get("name", ""))
        matched = False
        for have_name in have:
            if name == have_name or name in have_name or have_name in name:
                matched = True
                break
        if matched:
            have_items.append(item)
        else:
            shopping.append(item)
    return shopping, have_items


RECIPE_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "servings": {"type": "integer"},
        "estimated_time_minutes": {"type": "integer"},
        "cuisine": {"type": "string"},
        "ingredients": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "quantity": {"type": "string"},
                    "unit": {"type": "string"},
                    "note": {"type": "string"},
                },
                "required": ["name"],
            },
        },
        "steps": {"type": "array", "items": {"type": "string"}},
        "nutrition": {
            "type": "object",
            "properties": {
                "calories": {"type": "integer"},
                "protein_grams": {"type": "number"},
                "fat_grams": {"type": "number"},
                "carbohydrates_grams": {"type": "number"},
            },
        },
        "tips": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["title", "ingredients", "steps"],
}


def build_prompt(
    user_query: str,
    available: List[str],
    servings: str,
    cuisine: str,
    time_pref: str,
) -> str:
    parts = [
        "Generate one excellent cooking recipe as JSON.",
        "Follow this JSON schema strictly:",
        json.dumps(RECIPE_JSON_SCHEMA),
        "Constraints:",
        "- Keep ingredient names simple and common (no brand names).",
        "- Provide clear step-by-step instructions.",
        "- Use metric or common US units appropriately.",
        "- Keep the title short, around 4-5 words.",
    ]
    if user_query:
        parts.append(f"User request: {user_query}")
    if available:
        parts.append(
            "These ingredients are available at home; prefer using them where reasonable: "
            + ", ".join(available)
        )
    if servings:
        parts.append(f"Target servings: {servings}")
    if cuisine:
        parts.append(f"Preferred cuisine: {cuisine}")
    if time_pref:
        parts.append(f"Time preference: {time_pref}")
    parts.append("Return ONLY JSON. No markdown, no code fences, no commentary.")
    return "\n".join(parts)


def safe_json_from_text(text: str) -> Dict[str, Any]:
    """Attempt to extract JSON object from text."""
    # Trim code fences if present
    fence = re.compile(r"^\s*```(?:json)?\s*(.*)\s*```\s*$", re.DOTALL)
    m = fence.match(text)
    if m:
        text = m.group(1)
    # Find first { ... } block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]
    return json.loads(text)
