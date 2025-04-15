"""
Punto de entrada principal para la aplicación UpdateMe.
Configura la aplicación Flask y registra todas las rutas y middleware.
"""
import os
import sys
from flask import Flask, request
from flask import session
from flask_babel import Babel
from dotenv import load_dotenv
from api.routes import register_routes

# Asegurar que el directorio raíz está en el path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Cargar variables de entorno
load_dotenv()

# Crear y configurar la aplicación Flask
app = Flask(__name__, 
            template_folder="../templates",
            static_folder="../static",
            static_url_path="/static")
            
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "development-key-change-in-production"
)
app.config["BABEL_DEFAULT_LOCALE"] = "es"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "../translations"

# Configurar Babel para internacionalización
babel = Babel(app)

@babel.localeselector
def get_locale():
    # Primero intenta obtener el idioma de la sesión
    if "language" in session:
        return session["language"]
    # Si no hay idioma en la sesión, usa el del navegador
    return request.accept_languages.best_match(["es", "en"])

# Registrar las rutas
register_routes(app)

# Para ejecución directa y compatibilidad con Vercel
if __name__ == "__main__":
    app.run(debug=True)
