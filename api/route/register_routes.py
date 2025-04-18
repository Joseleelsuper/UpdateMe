from flask import request, jsonify
from flask_babel import gettext as _
from api.service.user_services import (
    validate_email, validate_username, validate_password,
    check_existing_email, create_new_user, update_existing_user
)


def register_register_routes(app):
    """Register user registration routes."""

    @app.route("/register", methods=["POST"])
    def register_user():
        data = request.get_json()
        username = data.get("username", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        # Validar datos del usuario
        username_error = validate_username(username)
        if username_error:
            return username_error
        
        email_error = validate_email(email)
        if email_error:
            return email_error
            
        password_error = validate_password(password)
        if password_error:
            return password_error

        # Comprobar si el correo ya existe
        existing_user = check_existing_email(email)

        try:
            if existing_user:
                # Si el usuario ya existe pero no tiene contraseña (solo está suscrito al boletín)
                if not existing_user.get("password"):
                    # Actualizar el usuario existente con los datos faltantes
                    error = update_existing_user(existing_user, username, password)
                    if error:
                        return error
                    
                    return jsonify({
                        "success": True,
                        "message": _("registrationSuccessful")
                    })
                else:
                    # El usuario ya tiene una cuenta completa
                    return jsonify({
                        "success": False,
                        "message": _("emailExists")
                    }), 409
            else:
                # Crear nuevo usuario
                error = create_new_user(email, username, password, send_emails=True)
                if error:
                    return error

                return jsonify({
                    "success": True,
                    "message": _("registrationSuccessful")
                })
                
        except Exception as e:
            print(f"Error en el registro de usuario: {str(e)}")
            return jsonify({
                "success": False,
                "message": _("An unexpected error occurred. Please try again.")
            }), 500