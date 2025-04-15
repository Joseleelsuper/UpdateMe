"""
Este archivo contiene las rutas (endpoints) de la API.
"""
from bson import ObjectId
from flask import request, jsonify, render_template, send_from_directory, session, redirect, url_for
from flask_babel import gettext as _
from datetime import datetime, timezone
from api.database import users_collection
from api.utils import is_valid_email
from api.services import send_email, generate_news_summary
from models.user import User

def register_routes(app):
    """Registra todas las rutas de la aplicación en la instancia Flask."""
    
    @app.route("/")
    def home():
        return render_template('index.html', title=_("title_homepage"))

    @app.route("/static/<path:path>")
    def serve_static(path):
        return send_from_directory('static', path)

    @app.route("/change_language/<language>")
    def change_language(language):
        session['language'] = language
        return redirect(request.referrer or url_for('home'))
        
    @app.route("/subscribe", methods=["POST"])
    def subscribe():
        data = request.get_json()
        email = data.get("email", "").strip().lower()
        if not is_valid_email(email):
            return jsonify({"success": False, "message": "Correo inválido."}), 400
        # Comprobar si ya existe
        if users_collection.find_one({"email": email}):
            return jsonify(
                {"success": False, "message": "Este correo ya está suscrito."}
            ), 409

        # Generar resumen IA
        summary = generate_news_summary(email)

        # Preparar usuario para BD (pero aún no guardarlo)
        user_doc = User(
            _id=ObjectId(),
            username=email.split("@")[0],  # Default username based on email
            email=email,
            password="",
            created_at=datetime.now(timezone.utc),
            role="free",
            email_verified=False,
            account_status="active",
            billing_address=None,
            last_login=None,
            subscription=None,
            payment_methods=[],
        ).__dict__

        try:
            # Intentar enviar el correo
            send_email(
                email,
                "¡Bienvenido a UpdateMe! Resumen semanal de tecnología",
                summary
            )
            # Si llegamos aquí, el correo se envió correctamente,
            # ahora sí guardamos el usuario en la BD
            users_collection.insert_one(user_doc)

            return jsonify(
                {"success": True, "message": "¡Suscripción exitosa! Revisa tu correo."}
            )
        except Exception as e:
            print(f"Error al enviar correo: {str(e)}")
            return jsonify(
                {"success": False, "message": f"Error enviando el correo: {str(e)}"}
            ), 500