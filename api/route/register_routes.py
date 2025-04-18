from flask import request, jsonify, session, g
from bson import ObjectId
from datetime import datetime, timezone
import re
import bcrypt
from flask_babel import gettext as _
from api.database import users_collection
from api.utils import is_valid_email
from api.services import send_email, generate_news_summary, send_welcome_email
from models.user import User


def register_register_routes(app):
    """Register user registration routes."""

    @app.route("/register", methods=["POST"])
    def register_user():
        data = request.get_json()
        username = data.get("username", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        # Validar nombre de usuario (solo letras, números y espacios)
        if not username or not re.match(r'^[a-zA-Z0-9\s]+$', username):
            return jsonify({
                "success": False,
                "message": _("invalidUsername")
            }), 400

        # Validar correo electrónico
        if not is_valid_email(email):
            return jsonify({
                "success": False,
                "message": _("invalidEmail")
            }), 400

        # Comprobar si el correo ya existe
        existing_user = users_collection.find_one({"email": email})

        # Validar contraseña (mínimo 6 caracteres, 1 mayúscula, 1 minúscula, 1 número, 1 carácter especial)
        if len(password) < 6:
            return jsonify({
                "success": False,
                "message": _("passwordLength")
            }), 400
        if not re.search(r'[A-Z]', password):
            return jsonify({
                "success": False,
                "message": _("passwordUppercase")
            }), 400
        if not re.search(r'[a-z]', password):
            return jsonify({
                "success": False,
                "message": _("passwordLowercase")
            }), 400
        if not re.search(r'[0-9]', password):
            return jsonify({
                "success": False,
                "message": _("passwordNumber")
            }), 400
        if not re.search(r'[_\W]', password):
            return jsonify({
                "success": False,
                "message": _("passwordSpecial")
            }), 400

        # Generar hash de la contraseña
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Obtener el idioma actual del usuario
        current_language = session.get("language", g.get("locale", "es"))

        try:
            if existing_user:
                # Si el usuario ya existe pero no tiene contraseña (solo está suscrito al boletín)
                if not existing_user.get("password"):
                    # Actualizar el usuario existente con los datos faltantes
                    users_collection.update_one(
                        {"email": email},
                        {
                            "$set": {
                                "username": username,
                                "password": hashed_password,
                                "role": existing_user.get("role", "free"),
                                "email_verified": existing_user.get("email_verified", False),
                                "account_status": "active",
                                "language": current_language
                            }
                        }
                    )
                    
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
                user_doc = User(
                    _id=ObjectId(),
                    username=username,
                    email=email,
                    password=hashed_password,
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

                # Insertar usuario en la base de datos solo si los correos se envían correctamente
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
                        print(f"Error enviando resumen completo al nuevo usuario: {str(e)}")
                        return jsonify({
                            "success": False,
                            "message": _("An unexpected error occurred. Please try again.")
                        }), 500
                except Exception as e:
                    print(f"Error enviando correos de bienvenida al nuevo usuario: {str(e)}")
                    return jsonify({
                        "success": False,
                        "message": _("An unexpected error occurred. Please try again.")
                    }), 500

                users_collection.insert_one(user_doc)

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