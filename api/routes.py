"""
Este archivo contiene las rutas (endpoints) de la API.
"""
from bson import ObjectId
from flask import request, jsonify, render_template, send_from_directory, session, redirect, url_for, g
from flask_babel import gettext as _
from datetime import datetime, timezone
import threading
from api.database import users_collection
from api.utils import is_valid_email
from api.services import send_email, generate_news_summary, send_welcome_email
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
            return jsonify({"success": False, "message": _("Please enter a valid email.")}), 400
        
        # Comprobar si ya existe
        if users_collection.find_one({"email": email}):
            return jsonify(
            {"success": False, "message": _("This email is already subscribed.")}
            ), 409

        # Obtener el idioma actual del usuario desde la sesión
        current_language = session.get('language', g.get('locale', 'es'))
        
        # Preparar usuario para BD con el idioma correcto
        user_doc = User(
            _id=ObjectId(),
            username=email.split("@")[0],  # Default username based on email
            email=email,
            password="",
            created_at=datetime.now(timezone.utc),
            role="free",
            email_verified=False,
            account_status="active",
            language=current_language,  # Usar el idioma actual
            billing_address=None,
            last_login=None,
            subscription=None,
            payment_methods=[],
        ).__dict__

        try:
            # 1. Guardar usuario en la BD inmediatamente
            users_collection.insert_one(user_doc)
            
            # 2. Enviar correo de bienvenida ligero (no generado por IA)
            send_welcome_email(email)
            
            # 3. Iniciar un hilo separado para generar y enviar el resumen completo
            def send_full_summary():
                try:
                    summary = generate_news_summary(email)
                    send_email(
                        email,
                        "UpdateMe: Tu resumen semanal de tecnología e IA",
                        summary
                    )
                except Exception as e:
                    print(f"Error enviando resumen completo: {str(e)}")
            
            # Iniciar el proceso en segundo plano
            threading.Thread(target=send_full_summary).start()

            return jsonify(
                {"success": True, "message": _("Subscription successful! We have sent you a welcome email and you will receive your first summary shortly.")}
            )
        except Exception as e:
            print(f"Error en el proceso de suscripción: {str(e)}")
            return jsonify(
                {"success": False, "message": _("An unexpected error occurred. Please try again.")}
            ), 500

    @app.route("/api/translations", methods=["GET"])
    def get_translations():
        """Endpoint para obtener traducciones para JavaScript."""
        translations = {
            # Traducciones existentes
            "validEmail": _("Please enter a valid email."),
            "networkError": _("Network error. Please try again later."),
            "processing": _("Processing..."),
            "subscribeButton": _("Subscribe"),
            "subscriptionSuccess": _("Subscription successful! We have sent you a welcome email and you will receive your first summary shortly."),
            
            # Excepciones y mensajes de error
            "errors": {
                "general": _("An unexpected error occurred. Please try again."),
                "notFound": _("The requested resource was not found."),
                "serverError": _("Server error. Please try again later."),
                "unauthorized": _("You are not authorized to perform this action."),
                "forbidden": _("Access forbidden."),
                "validation": _("Please check the form for errors."),
                "duplicateEmail": _("This email is already subscribed."),
                "timeout": _("The request timed out. Please try again."),
                "invalidData": _("The provided data is invalid."),
                "paymentRequired": _("Payment is required to access this feature.")
            }
        }
        return jsonify(translations)