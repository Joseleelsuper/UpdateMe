from flask import Blueprint, jsonify
from flask_babel import gettext as _

# Crear el blueprint para las rutas de traducciones
translations_bp = Blueprint('translations', __name__)

@translations_bp.route("/api/translations", methods=["GET"])
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
        
        # Traducciones para las páginas legales
        "legalPages": {
            "termsAndConditions": _("Terms & Conditions"),
            "privacyPolicy": _("Privacy Policy"),
            "lastUpdated": _("Last updated"),
            "introduction": _("Introduction"),
            "definitions": _("Definitions and Key Terms"),
            "communications": _("Communications"),
            "subscriptions": _("Subscriptions"),
            "content": _("Content"),
            "freeTrial": _("Free Trial"),
            "feeChanges": _("Fee Changes"),
            "refunds": _("Refunds"),
            "accounts": _("Accounts"),
            "intellectualProperty": _("Intellectual Property"),
            "links": _("Links To Other Web Sites"),
            "termination": _("Termination"),
            "limitationOfLiability": _("Limitation Of Liability"),
            "disclaimer": _("Disclaimer"),
            "governingLaw": _("Governing Law"),
            "changes": _("Changes to Terms"),
            "contact": _("Contact Us"),
            "informationWeCollect": _("Information We Collect"),
            "howWeUseInfo": _("How We Use Your Information"),
            "logFiles": _("Log Files"),
            "cookies": _("Cookies and Web Beacons"),
            "thirdPartyServices": _("Third-Party Services"),
            "aiProviders": _("AI Providers"),
            "security": _("Security"),
            "childrenPrivacy": _("Children's Privacy"),
            "changesToPolicy": _("Changes to This Privacy Policy"),
            "yourRights": _("Your Rights"),
        },
        
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
