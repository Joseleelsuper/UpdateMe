from flask import request, jsonify, session, g
from bson import ObjectId
from datetime import datetime, timezone
from flask_babel import gettext as _
from api.database import users_collection
from api.utils import is_valid_email
from api.services import send_email, generate_news_summary, send_welcome_email
from models.user import User


def register_subscribe_routes(app):
    """Register subscription-related routes."""

    @app.route("/subscribe", methods=["POST"])
    def subscribe():
        data = request.get_json()
        email = data.get("email", "").strip().lower()
        if not is_valid_email(email):
            return jsonify(
                {"success": False, "message": _("Please enter a valid email.")}
            ), 400

        if users_collection.find_one({"email": email}):
            return jsonify(
                {"success": False, "message": _("This email is already subscribed.")}
            ), 409

        current_language = session.get("language", g.get("locale", "es"))

        user_doc = User(
            _id=ObjectId(),
            username=email.split("@")[0],
            email=email,
            password="",
            created_at=datetime.now(timezone.utc),
            role="free",
            email_verified=False,
            account_status="active",
            language=current_language,
            search_provider="tavily",
            ai_provider="groq",
            billing_address=None,
            last_login=None,
            subscription=None,
            payment_methods=[],
        ).__dict__

        try:
            send_welcome_email(email)
            try:
                summary = generate_news_summary(email)
                send_email(
                    email,
                    "UpdateMe: Tu resumen semanal de tecnología e IA",
                    summary,
                )
            except Exception as e:
                print(f"Error enviando resumen completo: {str(e)}")

            users_collection.insert_one(user_doc)

            return jsonify(
                {
                    "success": True,
                    "message": _(
                        "Subscription successful! We have sent you a welcome email and you will receive your first summary shortly."
                    ),
                }
            )
        except Exception as e:
            print(f"Error en el proceso de suscripción: {str(e)}")
            return jsonify(
                {
                    "success": False,
                    "message": _("An unexpected error occurred. Please try again."),
                }
            ), 500
