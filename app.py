import os
from typing import Dict, Any, List, Tuple
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from werkzeug.security import check_password_hash

# Google Gemini
import google.generativeai as genai
import auth_service
import recipe_service

load_dotenv()

app = Flask(__name__)
# Basic secret for flash messages (safe default). You may set FLASK_SECRET in .env
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-key")

# SQLite setup for user authentication
DB_PATH = os.path.join(app.instance_path, "auth.db")
os.makedirs(app.instance_path, exist_ok=True)


def init_db() -> None:
    auth_service.init_db(DB_PATH)


def get_user_by_email(email: str):
    return auth_service.get_user_by_email(DB_PATH, email)


# Initialize DB on startup
init_db()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    # Don't crash; allow UI to render a friendly warning
    pass


def get_model():
    return recipe_service.get_model()


def normalize_name(name: str) -> str:
    return recipe_service.normalize_name(name)


def parse_available_ingredients(raw: str) -> List[str]:
    return recipe_service.parse_available_ingredients(raw)


def diff_shopping_list(
    recipe_ingredients: List[Dict[str, Any]], available: List[str]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    return recipe_service.diff_shopping_list(recipe_ingredients, available)


RECIPE_JSON_SCHEMA: Dict[str, Any] = recipe_service.RECIPE_JSON_SCHEMA


def build_prompt(
    user_query: str, available: List[str], servings: str, cuisine: str, time_pref: str
) -> str:
    return recipe_service.build_prompt(
        user_query, available, servings, cuisine, time_pref
    )


def safe_json_from_text(text: str) -> Dict[str, Any]:
    return recipe_service.safe_json_from_text(text)


def authenticate_user(email: str, password: str) -> bool:
    return auth_service.authenticate_user(DB_PATH, email, password)


def create_user(name: str, email: str, password: str) -> bool:
    return auth_service.create_user(DB_PATH, name, email, password)


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
        flash(
            "Missing GOOGLE_API_KEY in .env. Please configure it to generate recipes.",
            "danger",
        )
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
