from datetime import datetime

from flask import Blueprint, current_app, jsonify, render_template, request
from flask_login import current_user, login_required
from google import genai

from models import AIChatMessage, db
from routes.user import format_timetable_for_ai


ai_chat_bp = Blueprint("ai_chat", __name__)


def save_chat_message(user_id, question, answer):
    # Chat history should not make the request fail if persistence has an issue.
    try:
        chat_message = AIChatMessage(user_id=user_id, question=question, answer=answer)
        db.session.add(chat_message)
        db.session.commit()
    except Exception:
        db.session.rollback()


@ai_chat_bp.route("/chat")
@login_required
def chat():
    # The AI chat is intended for students and their timetable only.
    if current_user.is_admin:
        return "AI chat is available for students only."

    recent_messages = (
        AIChatMessage.query.filter_by(user_id=current_user.id)
        .order_by(AIChatMessage.created_at.desc())
        .limit(10)
        .all()
    )
    messages = list(reversed(recent_messages))

    return render_template("chat.html", messages=messages)


@ai_chat_bp.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    # Admins do not have a student timetable context for AI answers.
    if current_user.is_admin:
        return jsonify({"error": "AI chat is available for students only."}), 403

    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Message is required."}), 400

    timetable_data = format_timetable_for_ai(current_user)
    current_day = datetime.now().strftime("%A")

    system_prompt = f"""You are a university timetable assistant.
Answer questions only based on the following timetable data.
Do not make up information.
If the answer is not available in the timetable, say that the information is not available.
Be concise and helpful.

Student's timetable:
{timetable_data}

Today is {current_day}."""

    api_key = current_app.config.get("GEMINI_API_KEY")
    model = current_app.config.get("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        reply = "AI assistant is not configured. Please set GEMINI_API_KEY in your .env file."
        save_chat_message(current_user.id, message, reply)
        return jsonify({"reply": reply})

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=f"{system_prompt}\n\nStudent question: {message}",
        )
        reply = response.text or "I could not generate a response."
    except Exception as e:
        print("Gemini API error type:", type(e).__name__)
        print("Gemini API error message:", str(e))
        reply = "Sorry, the AI assistant is temporarily unavailable."
        save_chat_message(current_user.id, message, reply)
        return jsonify({"reply": reply}), 500

    save_chat_message(current_user.id, message, reply)
    return jsonify({"reply": reply})
