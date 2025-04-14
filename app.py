from flask import Flask, render_template, send_from_directory, request, session, redirect, url_for
from flask_babel import Babel, gettext as _
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'development-key-change-in-production')
app.config['BABEL_DEFAULT_LOCALE'] = 'es'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

babel = Babel(app)

@babel.localeselector
def get_locale():
    # Primero intenta obtener el idioma de la sesión
    if 'language' in session:
        return session['language']
    # Si no hay idioma en la sesión, usa el del navegador
    return request.accept_languages.best_match(['es', 'en'])

@app.route('/')
def home():
    return render_template('index.html', title=_("title_homepage"))

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/change_language/<language>')
def change_language(language):
    session['language'] = language
    return redirect(request.referrer or url_for('home'))

if __name__ == '__main__':
    os.system('pybabel compile -d translations')
    app.run(debug=True)
