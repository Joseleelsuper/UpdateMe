from flask import request, jsonify
from flask_babel import gettext as _
from api.service.user_services import (
    validate_email, check_existing_email, create_new_user
)


def register_subscribe_routes(app):
    """Register subscription-related routes."""

    @app.route("/subscribe", methods=["POST"])
    def subscribe():
        data = request.get_json()
        email = data.get("email", "").strip().lower()
        
        # Validar formato del correo
        email_error = validate_email(email)
        if email_error:
            return email_error

        # Comprobar si el correo ya existe
        if check_existing_email(email):
            return jsonify(
                {"success": False, "message": _("This email is already subscribed.")}
            ), 409

        # Crear nuevo usuario (solo con email, sin contraseña ni username personalizado)
        error = create_new_user(email, send_emails=True)
        if error:
            return error

        return jsonify(
            {
                "success": True,
                "message": _(
                    "Subscription successful! We have sent you a welcome email and you will receive your first summary shortly."
                ),
            }
        )
