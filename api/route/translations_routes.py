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
        
        # Traducciones específicas para SEO
        "seo": {
            # Títulos SEO para cada página
            "title_homepage": _("UpdateMe - Newsletter Semanal de Tecnología e IA"),
            "title_register_page": _("Regístrate - UpdateMe Newsletter de Tecnología"),
            "title_login_page": _("Inicia Sesión - UpdateMe"),
            "title_terms_page": _("Términos y Condiciones - UpdateMe"),
            "title_privacy_page": _("Política de Privacidad - UpdateMe"),
            "title_pricing_page": _("Planes y Precios - UpdateMe"),
            
            # Meta descripciones SEO para cada página
            "meta_desc_homepage": _("UpdateMe: La newsletter semanal que te mantiene al día con la tecnología y la IA. Recibe los resúmenes más relevantes en tu correo."),
            "meta_desc_register": _("Regístrate en UpdateMe y recibe resúmenes semanales de tecnología e IA personalizados para ti."),
            "meta_desc_login": _("Accede a tu cuenta de UpdateMe y gestiona tu newsletter personalizada de tecnología e IA."),
            "meta_desc_terms": _("Términos y condiciones de uso de UpdateMe. Información legal sobre el uso de nuestra newsletter y servicios."),
            "meta_desc_privacy": _("Política de privacidad de UpdateMe. Conoce cómo gestionamos y protegemos tus datos personales."),
            "meta_desc_pricing": _("Conoce nuestros planes y precios para recibir resúmenes semanales de tecnología e IA. Escoge el que mejor se adapte a ti."),
            
            # Palabras clave SEO para cada página
            "meta_keywords_home": _("newsletter, tecnología, IA, inteligencia artificial, noticias tech, resumen semanal"),
            "meta_keywords_register": _("registro, cuenta, newsletter tecnología, IA personalizada"),
            "meta_keywords_login": _("login, acceso, cuenta, newsletter tecnología"),
            "meta_keywords_terms": _("términos, condiciones, legal, servicios, newsletter"),
            "meta_keywords_privacy": _("privacidad, protección de datos, política, newsletter, RGPD"),
            "meta_keywords_pricing": _("precios, planes, suscripción, newsletter tecnología, IA"),
            
            # Otros textos SEO importantes
            "breadcrumb_home": _("Inicio"),
            "breadcrumb_register": _("Registro"),
            "breadcrumb_login": _("Acceso"),
            "breadcrumb_terms": _("Términos"),
            "breadcrumb_privacy": _("Privacidad"),
            "breadcrumb_pricing": _("Precios"),
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
        
        # Traducciones específicas para la página de precios
        "pricing": {
            "choose_plan": _("Choose Your Plan"),
            "select_plan": _("Select the plan that best fits your needs and get the most out of UpdateMe."),
            "free": _("Free"),
            "month": _("month"),
            "year": _("year"),
            "basic_access": _("Basic access to UpdateMe newsletter"),
            "full_access_monthly": _("Full access with monthly billing"),
            "full_access_yearly": _("Full access with yearly billing"),
            "weekly_newsletter": _("Weekly AI-generated tech newsletter"),
            "default_ai_provider": _("Default AI provider for processing"),
            "default_search_settings": _("Default search settings"),
            "customizable_ai": _("Customizable AI providers"),
            "customizable_prompts": _("Customizable processing prompts"),
            "configurable_search": _("Configurable search options"),
            "priority_processing": _("Priority processing"),
            "sign_up_free": _("Sign Up for Free"),
            "subscribe_now": _("Subscribe Now"),
            "subscribe_save": _("Subscribe & Save"),
            "most_popular": _("Most Popular"),
            "best_value": _("Best Value"),
            "save": _("Save"),
            "monthly": _("Monthly"),
            "annual": _("Annual"),
            "faq_title": _("Frequently Asked Questions"),
            "faq_what_included": _("What is included in all plans?"),
            "faq_included_answer": _("All plans include our weekly AI-curated tech and AI news newsletter delivered to your inbox."),
            "faq_differences": _("What are the differences between plans?"),
            "faq_differences_answer": _("Premium plans (Monthly and Annual) allow you to fully customize your experience by selecting different AI providers, customizing prompts, and configuring search settings to tailor your newsletter exactly how you want it."),
            "faq_upgrade": _("Can I upgrade anytime?"),
            "faq_upgrade_answer": _("Yes, you can upgrade from a Free plan to a Premium plan at any time from your dashboard."),
            "faq_cancel": _("How do I cancel my subscription?"),
            "faq_cancel_answer": _("You can cancel your subscription anytime from your account settings. Your premium features will remain active until the end of your current billing period.")
        }
    }
    return jsonify(translations)
