import json
import types

from lib import recipe_service


def test_get_model(monkeypatch):
    # Replace the GenerativeModel with a fake to capture init args
    captured = []

    class FakeModel:
        def __init__(self, model_name, system_instruction):
            captured.append(
                {
                    "model_name": model_name,
                    "system_instruction": system_instruction,
                }
            )

    mock_genai = types.SimpleNamespace(GenerativeModel=FakeModel)
    monkeypatch.setattr(recipe_service, "genai", mock_genai, raising=True)

    # Default when GEMINI_MODEL is not set
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    _m1 = recipe_service.get_model()
    assert captured[-1]["model_name"] == "gemini-1.5-flash"
    assert "Recipe Genie" in captured[-1]["system_instruction"]

    # With GEMINI_MODEL override
    monkeypatch.setenv("GEMINI_MODEL", "my-custom-model")
    _m2 = recipe_service.get_model()
    assert captured[-1]["model_name"] == "my-custom-model"


def test_normalize_name():
    assert recipe_service.normalize_name("  Garlic cloves.  ") == "garlic clove"
    assert recipe_service.normalize_name("Tomatoes") == "tomatoe"  # simple plural trim
    assert recipe_service.normalize_name("Fresh-basil!!") == "fresh-basil"


def test_parse_available_ingredients():
    raw = "tomatoes, onions\n garlic cloves ,\n\n Basil"
    parsed = recipe_service.parse_available_ingredients(raw)
    assert parsed == ["tomatoe", "onion", "garlic clove", "basil"]


def test_diff_shopping_list():
    recipe_ingredients = [
        {"name": "tomato", "quantity": "2"},
        {"name": "red onion", "quantity": "1"},
        {"name": "garlic", "quantity": "3 cloves"},
        {"name": "olive oil", "quantity": "2 tbsp"},
    ]
    available_raw = "tomatoes, onion\n garlic cloves"
    available = recipe_service.parse_available_ingredients(available_raw)

    shopping, have_items = recipe_service.diff_shopping_list(
        recipe_ingredients, available
    )

    have_names = {item["name"] for item in have_items}
    shop_names = {item["name"] for item in shopping}

    assert have_names == {"tomato", "red onion", "garlic"}
    assert shop_names == {"olive oil"}


def test_build_prompt():
    prompt = recipe_service.build_prompt(
        user_query="Pasta with tomato",
        available=["garlic", "basil"],
        servings="2",
        cuisine="italian",
        time_pref="30 minutes",
    )

    # Contains core guidance and schema
    assert "Generate one excellent cooking recipe as JSON." in prompt
    assert json.dumps(recipe_service.RECIPE_JSON_SCHEMA) in prompt

    # Contains user-provided context
    assert "User request: Pasta with tomato" in prompt
    assert (
        "These ingredients are available at home; prefer using them where reasonable: garlic, basil"
        in prompt
    )
    assert "Target servings: 2" in prompt
    assert "Preferred cuisine: italian" in prompt
    assert "Time preference: 30 minutes" in prompt
    assert "Return ONLY JSON. No markdown, no code fences, no commentary." in prompt


def test_safe_json_from_text():
    fenced = """
```json
{"title": "My Dish", "ingredients": [{"name": "salt"}], "steps": ["do a"]}
```
""".strip()
    data1 = recipe_service.safe_json_from_text(fenced)
    assert data1["title"] == "My Dish"
    assert data1["ingredients"][0]["name"] == "salt"
    assert data1["steps"] == ["do a"]

    wrapped = 'Here is the recipe: {"title": "Soup", "ingredients": [], "steps": ["boil"]} Thanks!'
    data2 = recipe_service.safe_json_from_text(wrapped)
    assert data2["title"] == "Soup"
    assert data2["steps"] == ["boil"]
