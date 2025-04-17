"""
Implementación de OpenAI como proveedor de IA.
"""

from bson import Regex
import openai
from typing import Dict, Any

from .prompts import (
    get_email_template,
    get_fallback_content,
    get_news_summary_prompt,
)

from .base_provider import BaseAIProvider
from ..cache_manager import CacheManager
from ..database import db


class OpenAIProvider(BaseAIProvider):
    """
    Implementación del proveedor de IA OpenAI.
    """

    def __init__(self, api_key: str, **kwargs):
        """
        Inicializa el proveedor de IA OpenAI.

        Args:
            api_key: La clave API de OpenAI
            kwargs: Parámetros adicionales como modelo
        """
        super().__init__(api_key, **kwargs)
        openai.api_key = api_key
        self.model = kwargs.get("model", "gpt-4o-mini")

    def generate_content(self, prompt: str, **kwargs) -> str:
        """
        Genera contenido utilizando la API de OpenAI.

        Args:
            prompt: El prompt para generar contenido
            kwargs: Parámetros adicionales como temperatura y system_content

        Returns:
            El contenido generado como string
        """
        try:
            temperature = kwargs.get("temperature", 0.7)
            system_content = kwargs.get("system_content", "")

            # Verificar caché
            cache_params = {
                "system_content": system_content,
                "temperature": temperature,
            }
            cache_key = CacheManager.generate_cache_key(
                prompt, "openai_content", cache_params
            )
            cached_content = CacheManager.get_from_cache(cache_key)

            if cached_content:
                print("Contenido recuperado de caché para prompt similar")
                return str(cached_content)

            messages = []
            if system_content:
                messages.append({"role": "system", "content": system_content})

            messages.append({"role": "user", "content": prompt})

            response = openai.chat.completions.create(
                model=self.model, messages=messages, temperature=temperature
            )

            content = response.choices[0].message.content
            result = content if content is not None else ""

            # Guardar en caché
            CacheManager.save_to_cache(
                cache_key=cache_key,
                response=result,
                provider_type="openai_content",
                query=prompt,
            )

            return result
        except Exception as e:
            print(f"Error generando contenido con OpenAI: {str(e)}")
            return f"Error: {str(e)}"

    def search_web(self, query: str) -> Dict[str, Any]:
        """
        Realiza una búsqueda web utilizando las capacidades integradas de OpenAI.

        Args:
            query: La consulta de búsqueda

        Returns:
            Resultados procesados de la búsqueda
        """
        # Verificar caché
        cache_key = CacheManager.generate_cache_key(query, "openai_web_search")
        cached_result = CacheManager.get_from_cache(cache_key)

        if cached_result:
            print(f"Resultado recuperado de caché para: {query}")
            return cached_result

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": query}],
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "web_search",
                            "parameters": {
                                "type": "object",
                                "properties": {"query": {"type": "string"}},
                                "required": ["query"],
                            },
                        },
                    }
                ],
                tool_choice="auto",
            )

            result = {"content": response.choices[0].message.content, "success": True}

            # Guardar en caché
            CacheManager.save_to_cache(
                cache_key=cache_key,
                response=result,
                provider_type="openai_web_search",
                query=query,
            )

            return result
        except Exception as e:
            print(f"Error en búsqueda web con OpenAI: {str(e)}")
            return {"error": str(e), "success": False}

    def generate_news_summary(self, email: str) -> str:
        """
        Genera un resumen de noticias personalizado para el usuario.

        Args:
            email: El email del usuario

        Returns:
            El resumen de noticias formateado como un email
        """
        # Extraer username y obtener el idioma del usuario desde la base de datos

        username = email.split("@")[0]

        # Buscar al usuario en la base de datos
        user_data = db.users.find_one({"email": Regex(f"^{email}$", "i")})
        language = user_data.get("language", "es") if user_data else "es"

        # Crear consulta para buscar noticias de tecnología e IA
        query = "Latest technology and AI news this week, top 5 most important news"

        try:
            # Realizar la búsqueda web y generación de contenido
            search_result = self.search_web(query)

            if not search_result.get("success", False):
                return get_fallback_content(username, language)

            # Procesar los resultados para generar un resumen bien formateado
            system_prompt = get_news_summary_prompt(language)

            news_content = self.generate_content(
                prompt=search_result.get("content", ""), system_content=system_prompt
            )

            # Formatear el email final con el contenido generado
            return get_email_template(username, news_content, language)

        except Exception as e:
            print(f"Error al generar contenido con OpenAI: {str(e)}")
            return get_fallback_content(username, language)

    def _generate_fallback_content(self, email: str) -> str:
        """
        Genera un contenido de respaldo cuando falla la generación con IA.

        Args:
            email: Email del usuario

        Returns:
            str: Contenido de respaldo
        """
        # Extraer username y obtener el idioma del usuario desde la base de datos

        username = email.split("@")[0]

        # Buscar al usuario en la base de datos
        user_data = db.users.find_one({"email": Regex(f"^{email}$", "i")})
        language = user_data.get("language", "es") if user_data else "es"

        return get_fallback_content(username, language)
