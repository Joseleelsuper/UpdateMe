from flask import render_template, send_from_directory, session, redirect, request, url_for
from flask_babel import gettext as _


def register_page_routes(app):
    """Register page-related routes."""
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
