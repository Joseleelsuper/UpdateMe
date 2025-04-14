import os
from bson import ObjectId
from flask import (
    Flask,
    render_template,
    send_from_directory,
    request,
    session,
    redirect,
    url_for,
    jsonify,
)
from flask_babel import Babel, gettext as _
import re
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timezone
import resend
from dotenv import load_dotenv

from models.user import User

# Cargar variables de entorno
load_dotenv(".env")

# Configuración MongoDB
MONGODB_URI = os.environ.get("MONGODB_URI")
client = MongoClient(MONGODB_URI, server_api=ServerApi("1"))
db = client["updateme"]
users_collection = db["users"]

# Configuración Resend
resend.api_key = os.environ.get("RESEND_API_KEY")

# --- Utilidad para validar email ---
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


def is_valid_email(email):
    return EMAIL_REGEX.match(email) is not None


# --- Utilidad para IA (Groq, OpenAI, etc) ---
def generate_news_summary(email, provider="groq"):
    """
    Genera un resumen de noticias tecnológicas de la última semana usando IA.
    Por defecto usa Groq, pero se puede cambiar el proveedor fácilmente.
    """
    # Aquí deberías implementar la llamada real a la API de Groq, OpenAI, etc.
    # Por ahora, devuelve un texto simulado.
    return f"Hola {email},\n\nAquí tienes un resumen de las noticias tecnológicas más importantes de la última semana:\n\n- Noticia 1: ...\n- Noticia 2: ...\n- Noticia 3: ...\n\n¡Gracias por suscribirte a UpdateMe!"


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "development-key-change-in-production"
)
app.config["BABEL_DEFAULT_LOCALE"] = "es"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"

babel = Babel(app)


@babel.localeselector
def get_locale():
    # Primero intenta obtener el idioma de la sesión
    if "language" in session:
        return session["language"]
    # Si no hay idioma en la sesión, usa el del navegador
    return request.accept_languages.best_match(["es", "en"])


@app.route("/")
def home():
    return render_template("index.html", title=_("title_homepage"))


@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)


@app.route("/change_language/<language>")
def change_language(language):
    session["language"] = language
    return redirect(request.referrer or url_for("home"))


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
    
    # Enviar correo con Resend antes de guardar en BD
    params = {
        "from": "UpdateMe <onboarding@resend.dev>",  # Usar el remitente verificado de Resend
        "to": [email],
        "subject": "¡Bienvenido a UpdateMe! Resumen semanal de tecnología",
        "text": summary,
    }
    
    try:
        # Intentar enviar el correo
        resend.Emails.send(**params)
        users_collection.insert_one(user_doc)
        
        return jsonify(
            {"success": True, "message": "¡Suscripción exitosa! Revisa tu correo."}
        )
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
        return jsonify(
            {"success": False, "message": f"Error enviando el correo: {str(e)}"}
        ), 500


if __name__ == "__main__":
    os.system("pybabel compile -d translations")
    app.run(debug=True)
