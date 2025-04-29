from dataclasses import dataclass, field
from typing import List, Optional, Literal
from datetime import datetime
from bson import ObjectId


@dataclass
class User:
    """Modelo de usuario para la base de datos MongoDB.
    Este modelo representa la estructura de un usuario en la base de datos y contiene
    información relevante como el nombre de usuario, correo electrónico, fecha de creación,
    rol, estado de la cuenta, entre otros.
    """

    _id: ObjectId
    """ID único del usuario en la base de datos."""

    username: str
    """Nombre de usuario.
    
    Puede estar repetido, ya que no se depende de este campo para la autenticación.
    """

    email: str
    """Correo electrónico del usuario.

    Es único y se utiliza para la autenticación y recuperación de contraseña.
    """

    created_at: datetime
    """Fecha de creación del usuario en la base de datos.
    
    No representa nada importante, ya que puede desaparecer y cambiar si el
    usuario decide eliminar su cuenta y volver a registrarse con el mismo correo.
    """

    role: Literal["free", "paid", "admin"]
    """Rol del usuario en la aplicación.

    De normal siempre será "free". Para obtener el rol "paid" se debe pagar una
    suscripción. El rol "admin" es para los administradores de la aplicación.
    """

    email_verified: bool
    """Indica si el correo electrónico del usuario ha sido verificado.

    TODO: Implementar verificación de correo electrónico.
    """

    account_status: Literal["active", "suspended"]
    """Estado de la cuenta del usuario.

    active: La cuenta está activa y el usuario recibirá correos electrónicos.

    suspended: La cuenta ha sido suspendida y no recibirá más correos electrónicos
    hasta que se reactive desde la web.
    """

    language: str = "es"
    """Idioma del usuario.

    Por defecto suponemos que el idioma es español. Se puede cambiar a inglés o español.

    El usuario al registrarse podrá elegir el idioma que desee.
    """

    search_provider: Literal["serpapi", "tavily"] = "tavily"
    """Proveedor de búsqueda utilizado por el usuario.

    tavily: Proveedor de búsqueda por defecto. https://app.tavily.com/

    serapi: Proveedor de búsqueda de Google. https://serpapi.com/
    """

    ai_provider: Literal["openai", "deepseek", "groq"] = "groq"
    """Proveedor de IA utilizado por el usuario.

    openai: Proveedor de IA de OpenAI. https://openai.com/

    deepseek: Proveedor de IA de DeepSeek. https://deepseek.ai/

    groq: Proveedor de IA de Groq. https://groq.com/

    Por defecto es groq ya que es gratuito.
    """

    password: Optional[str] = None
    """Contraseña del usuario.

    Puede ser NULL debido a que el usuario puede simplemente suscribirse al boletín sin registrarse.    
    """

    billing_address: Optional[ObjectId] = None
    """Dirección de facturación del usuario."""

    last_login: Optional[datetime] = None
    """Último inicio de sesión del usuario.

    Se usa con fines estadísticos y por curiosidad.
    """

    subscription: Optional[ObjectId] = None
    """Suscripción de pago del usuario."""

    payment_methods: List[ObjectId] = field(default_factory=list)
    """Métodos de pago del usuario."""

    prompts: Optional[ObjectId] = None
    """Prompts personalizados del usuario."""

    last_email_sent: Optional[datetime] = None
    """Último correo electrónico enviado al usuario.

    Permite enviar cada semana un correo electrónico al usuario con información relevante.
    """
