from flask import jsonify
from flask_babel import gettext as _


def register_translations_routes(app):
    """Register translations API route for client-side."""

    @app.route("/api/translations", methods=["GET"])
    def get_translations():
        translations = {
            "validEmail": _("Please enter a valid email."),
            "networkError": _("Network error. Please try again later."),
            "processing": _("Processing..."),
            "subscribeButton": _("Subscribe"),
            "subscriptionSuccess": _(
                "Subscription successful! We have sent you a welcome email and you will receive your first summary shortly."
            ),
            
            "invalidUsername": _("invalidUsername"),
            "invalidEmail": _("invalidEmail"),  
            "passwordLength": _("passwordLength"),
            "passwordUppercase": _("passwordUppercase"),
            "passwordLowercase": _("passwordLowercase"),
            "passwordNumber": _("passwordNumber"),
            "passwordSpecial": _("passwordSpecial"),
            "registrationSuccessful": _("registrationSuccessful"),
            "emailExists": _("emailExists"),
            "Register": _("Register"),
            
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
                "paymentRequired": _("Payment is required to access this feature."),
            },
        }
        return jsonify(translations)
