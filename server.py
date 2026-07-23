import hashlib
import os
import secrets

import flask
from authlib.integrations.flask_client import OAuth

from database import (
    DB_LOCK,
    conn,
    cursor,
    new_conversation_id,
    redact_personal_data,
    save_anonymized_chat,
)
from manager import add_error, add_request, generate_response, get_stats, start_manager


app = flask.Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)

# Put FLASK_SECRET_KEY in .env later for permanent login sessions.
app.secret_key = os.getenv("FLASK_SECRET_KEY") or secrets.token_urlsafe(32)

start_manager()

USERS = {}
SETTINGS = {}
PREMIUM_USERS = set()

UPI_ID = "+91 70017 42835"
ADMIN_EMAIL = "bhoivaidik@gmail.com"

MOODS = {
    "normal": "You are Cognit AI. Be helpful and balanced.",
    "study": "You are a teacher.",
    "coding": "You are a programmer.",
    "creative": "Be creative.",
    "business": "Be professional.",
}


def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()


oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=os.getenv("client_id_google"),
    client_secret=os.getenv("client_secret_google"),
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    client_kwargs={"scope": "email profile"},
)

github = oauth.register(
    name="github",
    client_id=os.getenv("gitsecret"),
    client_secret=os.getenv("Git"),
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={
        "scope": "user:email",
        "headers": {"Accept": "application/json"},
    },
)


@app.route("/")
def home():
    user = flask.session.get("user")
    guest = flask.session.get("guest")

    if not user and not guest:
        return flask.redirect("/login")

    return flask.render_template("ui.html")


# @app.route("/login")
# def login_page():
#     return flask.render_template("ui.html")


@app.route("/guest")
def guest_login():
    flask.session["guest"] = True
    return flask.redirect("/")


@app.route("/login/apple")
def login_apple():
    return "Apple Login Coming Soon"


@app.route("/login/github")
def login_github():
    redirect_uri = flask.url_for("github_callback", _external=True)
    return github.authorize_redirect(redirect_uri)


@app.route("/auth/github/callback")
def github_callback():
    github.authorize_access_token()
    user = github.get("user").json()

    email = user.get("email")
    if not email:
        return flask.redirect("/login")

    flask.session["user"] = email
    return flask.redirect("/")


@app.route("/login/google")
def login_google():
    return google.authorize_redirect(
        flask.url_for("google_callback", _external=True)
    )


@app.route("/auth/google/callback")
def google_callback():
    google.authorize_access_token()
    user = google.get("userinfo").json()

    email = user.get("email")
    if not email:
        return flask.redirect("/login")

    flask.session["user"] = email
    return flask.redirect("/")


@app.route("/manager-data")
def get_manager_data():
    stats = get_stats()

    return flask.jsonify({
        "users": len(USERS),
        "premium": len(PREMIUM_USERS),
        "requests": stats["requests"],
        "errors": stats["errors"],
        "model_status": "Online",
        "logs": [
            "Server Started",
            "Manager Active",
            "AI Provider Manager Connected",
        ],
    })


@app.route("/library")
def library():
    return flask.render_template("library.html")


@app.route("/api/library")
def get_library():
    with DB_LOCK:
        cursor.execute("""
            SELECT id, title, author, price, rent_price
            FROM library
        """)
        books = cursor.fetchall()

    result = []

    for book in books:
        result.append({
            "id": book[0],
            "title": book[1],
            "author": book[2],
            "price": book[3],
            "rent_price": book[4],
        })

    return flask.jsonify(result)


@app.route("/api/library/buy", methods=["POST"])
def buy_book():
    return flask.jsonify({
        "success": True,
        "message": "Book purchased",
    })


@app.route("/api/library/rent", methods=["POST"])
def rent_book():
    return flask.jsonify({
        "success": True,
        "message": "Book rented",
    })


@app.route("/api/signup", methods=["POST"])
def signup():
    data = flask.request.get_json(silent=True) or {}

    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not username or not email or not password:
        return flask.jsonify({
            "success": False,
            "error": "Username, email, and password are required.",
        }), 400

    try:
        with DB_LOCK:
            cursor.execute("""
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
            """, (
                username,
                email,
                hash_pass(password),
            ))
            conn.commit()

        return flask.jsonify({"success": True})

    except Exception:
        return flask.jsonify({
            "success": False,
            "error": "That email is already registered.",
        }), 409


@app.route("/api/login", methods=["POST"])
def api_login():
    data = flask.request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    with DB_LOCK:
        cursor.execute("""
            SELECT id, username, email, password, premium
            FROM users
            WHERE email = ?
        """, (email,))
        user = cursor.fetchone()

    if not user or user[3] != hash_pass(password):
        return flask.jsonify({"success": False}), 401

    flask.session["user"] = email
    return flask.jsonify({"success": True})


@app.route("/api/account")
def account():
    email = flask.session.get("user")

    if not email:
        return flask.jsonify({"logged_in": False})

    with DB_LOCK:
        cursor.execute("""
            SELECT username, email, premium
            FROM users
            WHERE email = ?
        """, (email,))
        user = cursor.fetchone()

    if not user:
        flask.session.pop("user", None)
        return flask.jsonify({"logged_in": False})

    return flask.jsonify({
        "logged_in": True,
        "username": user[0],
        "email": user[1],
        "premium": bool(user[2]),
    })


@app.route("/chat", methods=["POST"])
def chat():
    data = flask.request.get_json(silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()
    mood = data.get("mood", "normal")
    user = flask.session.get("user", "guest")

    if not prompt:
        return flask.jsonify({"error": "Empty prompt"}), 400

    add_request()

    try:
        mood_text = MOODS.get(mood, MOODS["normal"])

        # Privacy: redact before saving, placing in browser session,
        # or sending conversation context to an AI provider.
        safe_prompt = redact_personal_data(prompt)

        if "conversation_id" not in flask.session:
            flask.session["conversation_id"] = new_conversation_id()

        conversation_id = flask.session["conversation_id"]

        existing_history = flask.session.get("chat_history", [])
        history = []

        for message in existing_history[-10:]:
            role = message.get("role")
            content = redact_personal_data(message.get("content", ""))

            if role in {"user", "assistant"} and content:
                history.append({
                    "role": role,
                    "content": content,
                })

        history.append({
            "role": "user",
            "content": safe_prompt,
        })

        history = history[-10:]

        save_anonymized_chat(
            conversation_id,
            "user",
            safe_prompt,
        )

        history_text = ""

        for message in history:
            if message["role"] == "user":
                history_text += f"User: {message['content']}\n"
            else:
                history_text += f"Assistant: {message['content']}\n"

        final_prompt = f"""
You are Cognit AI.

Rules:
- You were developed by the Cognit Team.
- Your name is Cognit.
- You are the official assistant of the EliteAI platform.
- Always follow the user's mood instructions.
- Do not request personal data.
- Do not reveal private details from chat history.

{mood_text}

# REDACTED CHAT MEMORY
{history_text}

User: {safe_prompt}
"""

        response = generate_response(final_prompt)
        safe_response = redact_personal_data(response)

        history.append({
            "role": "assistant",
            "content": safe_response,
        })

        flask.session["chat_history"] = history[-10:]

        save_anonymized_chat(
            conversation_id,
            "assistant",
            safe_response,
        )

        return flask.jsonify({
            "response": safe_response,
            "mood": mood,
            "user": user,
        })

    except Exception as error:
        add_error()
        print("SERVER ERROR:", error)

        return flask.jsonify({
            "response": "Sorry, Cognit AI is currently unavailable. Please try again.",
        }), 500


@app.route("/manager")
def manager_page():
    return flask.render_template("manager.html")


@app.route("/logout")
def logout():
    flask.session.pop("user", None)
    flask.session.pop("guest", None)
    flask.session.pop("chat_history", None)
    flask.session.pop("conversation_id", None)

    return flask.redirect("/login")


@app.route("/profile")
def profile():
    return flask.jsonify({
        "user": flask.session.get("user", "guest"),
    })


@app.route("/history")
def history():
    return flask.jsonify({
        "message": "Only anonymized conversation data is stored locally.",
    })


@app.route("/memory")
def memory():
    return flask.jsonify({
        "message": "Chat memory contains redacted content only.",
    })


@app.route("/donate")
def donate():
    return flask.jsonify({
        "upi": UPI_ID,
    })


@app.route("/api/settings", methods=["POST"])
def save_settings():
    data = flask.request.get_json(silent=True) or {}
    user = flask.session.get("user")

    if not user:
        return flask.jsonify({"success": False}), 401

    SETTINGS[user] = data
    return flask.jsonify({"success": True})


@app.route("/api/premium")
def premium_status():
    user = flask.session.get("user")

    return flask.jsonify({
        "premium": user in PREMIUM_USERS,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)