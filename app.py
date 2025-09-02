import os
import json
import re
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Tuple
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Google Gemini
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)
# Basic secret for flash messages (safe default). You may set FLASK_SECRET in .env
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-key")

# SQLite setup for user authentication
DB_PATH = os.path.join(app.instance_path, "auth.db")
os.makedirs(app.instance_path, exist_ok=True)


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def get_user_by_email(email: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT id, name, email, password_hash, created_at FROM users WHERE email = ?",
            (email,),
        )
        return cur.fetchone()


# Initialize DB on startup
init_db()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    # Don't crash; allow UI to render a friendly warning
    pass


def get_model():
    """Configure and return a Gemini model instance."""
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
    # Simple plural trim
    if s.endswith("es") and len(s) > 3:
        s = s[:-2]
    elif s.endswith("s") and len(s) > 2:
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


def diff_shopping_list(recipe_ingredients: List[Dict[str, Any]], available: List[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Return (shopping_list, have_list). Match by normalized ingredient name containment.
    """
    # Ensure all items in available are strings to avoid unhashable type error
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
          "note": {"type": "string"}
        },
        "required": ["name"]
      }
    },
    "steps": {"type": "array", "items": {"type": "string"}},
    "nutrition": {
      "type": "object",
      "properties": {
        "calories": {"type": "integer"},
        "protein_grams": {"type": "number"},
        "fat_grams": {"type": "number"},
        "carbohydrates_grams": {"type": "number"}
      }
    },
    "tips": {"type": "array", "items": {"type": "string"}}
  },
  "required": ["title", "ingredients", "steps"]
}


def build_prompt(user_query: str, available: List[str], servings: str, cuisine: str, time_pref: str) -> str:
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




def authenticate_user(email: str, password: str) -> bool:
    """Authenticate using SQLite (passwords are hashed)."""
    row = get_user_by_email(email)
    if not row:
        return False
    return check_password_hash(row["password_hash"], password)


def create_user(name: str, email: str, password: str) -> bool:
    """Create a new user in SQLite (stores hashed password)."""
    password_hash = generate_password_hash(password)
    created_at = datetime.utcnow().isoformat()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (name, email, password_hash, created_at),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Email already exists
        return False


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            # flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/home", methods=["GET"])
@login_required
def home():
    return render_template(
        "index.html",
        has_api_key=bool(GOOGLE_API_KEY),
    )

@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        remember = request.form.get("remember")
        
        if not email or not password:
            flash("Please enter both email and password.", "warning")
            return render_template("login.html")
        
        row = get_user_by_email(email)
        if row and check_password_hash(row["password_hash"], password):
            session["user_email"] = row["email"]
            session["user_name"] = row["name"]
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password.", "danger")
            return render_template("login.html")
    
    return render_template("login.html")


# Disabling for now.
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        agree_terms = request.form.get("agree_terms")
        
        # Validation
        if not all([name, email, password, confirm_password]):
            flash("Please fill in all fields.", "warning")
            return render_template("register.html")
        
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")
        
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "warning")
            return render_template("register.html")
        
        if not agree_terms:
            flash("Please agree to the Terms of Service.", "warning")
            return render_template("register.html")
        
        # Create user
        if create_user(name, email, password):
            session["user_email"] = email
            session["user_name"] = name
            session["logged_in"] = True
            
            flash(f"Account created successfully! Welcome, {name}!", "success")
            return redirect(url_for("index"))
        else:
            flash("An account with this email already exists.", "danger")
            return render_template("register.html")
    
    return render_template("register.html")


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        
        if not email:
            flash("Please enter your email address.", "warning")
            return render_template("forgot_password.html")
        
        row = get_user_by_email(email)
        if row:
            # In production, send actual email with reset link
            flash("Password reset instructions have been sent to your email.", "info")
            return redirect(url_for("login"))
        else:
            flash("No account found with this email address.", "danger")
            return render_template("forgot_password.html")
    
    return render_template("forgot_password.html")


@app.route("/logout")
def logout():
    session.clear()
    # flash("You have been logged out successfully.", "info")
    return redirect(url_for("index"))


@app.route("/generate", methods=["POST"])
@login_required
def generate():
    if not GOOGLE_API_KEY:
        flash("Missing GOOGLE_API_KEY in .env. Please configure it to generate recipes.", "danger")
        return redirect(url_for("index"))

    user_query = request.form.get("recipe_prompt", "").strip()
    available_raw = request.form.get("available_ingredients", "").strip()
    servings = request.form.get("servings", "").strip()
    cuisine = request.form.get("cuisine", "").strip()
    time_pref = request.form.get("time_pref", "").strip()

    available = parse_available_ingredients(available_raw)

    model = get_model()
    generation_config = {
        "temperature": 0.8,
        "top_p": 0.95,
        "top_k": 40,
        "response_mime_type": "application/json",
        "response_schema": RECIPE_JSON_SCHEMA,
    }

    prompt = build_prompt(user_query, available, servings, cuisine, time_pref)

    try:
        response = model.generate_content(prompt, generation_config=generation_config)

        text = response.text
        recipe = safe_json_from_text(text)
    except Exception as e:
        flash(f"Failed to generate or parse recipe: {e}", "danger")
        return redirect(url_for("index"))

    # Ensure basic fields exist
    recipe.setdefault("title", "Your Custom Recipe")
    recipe.setdefault("ingredients", [])
    recipe.setdefault("steps", [])

    shopping, have_items = diff_shopping_list(recipe.get("ingredients", []), available)

    return render_template(
        "result.html",
        query=user_query,
        available=available,
        recipe=recipe,
        shopping_list=shopping,
        have_items=have_items,
    )


if __name__ == "__main__":
    app.run(debug=True)

