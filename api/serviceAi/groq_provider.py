"""
Implementación de Groq como proveedor de IA.
"""

import json
import re
from typing import Dict, Any
from openai import OpenAI

from .base_provider import BaseAIProvider
from .serpapi_provider import SerpAPIProvider
from .talivy_provider import TavilyProvider
from .prompts import get_web_search_prompt, get_keyword_extraction_prompt
from ..cache_manager import CacheManager


class GroqProvider(BaseAIProvider):
    """
    Implementación del proveedor de IA Groq.
    """

    def __init__(self, api_key: str, **kwargs):
        """
        Inicializa el proveedor de IA Groq.

        Args:
            api_key: La clave API de Groq
            kwargs: Parámetros adicionales como modelo y clave API de búsqueda
        """
        super().__init__(api_key, **kwargs)
        self.model = kwargs.get("model", "llama3-70b-8192")

        # Configurar el proveedor de búsqueda seleccionado
        if self.search_provider_type.lower() == "tavily" and self.tavily_key:
            self.search_provider = TavilyProvider(
                self.tavily_key,
                search_depth=self.tavily_search_depth,
                topic=self.tavily_topic,
                time_range=self.tavily_time_range,
                include_raw_content=self.tavily_include_raw_content
            )
        elif self.serpapi_key:
            self.search_provider = SerpAPIProvider(self.serpapi_key)

        # Inicializar cliente de Groq
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1",
        )

    def generate_content(self, prompt: str, **kwargs) -> str:
        """
        Genera contenido utilizando la API de Groq.

        Args:
            prompt: El prompt para generar contenido
            kwargs: Parámetros adicionales como temperatura

        Returns:
            El contenido generado como string
        """
        # Verificar caché para prompts generales
        system_content = kwargs.get("system_content", "")
        temperature = kwargs.get("temperature", 0.7)

        cache_params = {"system_content": system_content, "temperature": temperature}

        cache_key = CacheManager.generate_cache_key(
            prompt, "groq_content", cache_params
        )
        cached_content = CacheManager.get_from_cache(cache_key)

        if (cached_content):
            print("Contenido recuperado de caché para prompt similar")
            return str(cached_content)

        try:
            messages = []
            if system_content:
                messages.append({"role": "system", "content": system_content})

            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=temperature
            )

            content = response.choices[0].message.content
            result = content if content is not None else ""

            # Guardar en caché
            CacheManager.save_to_cache(
                cache_key=cache_key,
                response=result,
                provider_type="groq_content",
                query=prompt,
            )

            return result
        except Exception as e:
            print(f"Error generando contenido con Groq: {str(e)}")
            return f"Error: {str(e)}"

    def search_web(self, query: str) -> Dict[str, Any]:
        """
        Realiza una búsqueda web utilizando el proveedor configurado y procesa los resultados con Groq.

        Args:
            query: La consulta de búsqueda

        Returns:
            Resultados procesados de la búsqueda
        """
        from api.database import db
        from api.auth import get_current_user_id
        from bson import ObjectId
        
        # Inicializar el proveedor de búsqueda si no está configurado o si ha cambiado el tipo
        if self.search_provider_type == "tavily" and self.tavily_key and not isinstance(self.search_provider, TavilyProvider):
            self.search_provider = TavilyProvider(
                self.tavily_key,
                search_depth=self.tavily_search_depth,
                topic=self.tavily_topic,
                time_range=self.tavily_time_range,
                include_raw_content=self.tavily_include_raw_content
            )
        elif self.search_provider_type == "serpapi" and self.serpapi_key and not isinstance(self.search_provider, SerpAPIProvider):
            self.search_provider = SerpAPIProvider(self.serpapi_key)
        
        # Si no tenemos proveedor de búsqueda, volvemos al método de simulación
        if not self.search_provider:
            return self._simulate_web_search(query)

        # Verificar caché primero
        cache_key = CacheManager.generate_cache_key(query, "groq_web_search")
        cached_result = CacheManager.get_from_cache(cache_key)
        if cached_result:
            print(f"Resultado recuperado de caché para: {query}")
            return cached_result

        try:
            # Obtener la configuración personalizada del usuario si está disponible
            user_config = None
            user_id = None
            try:
                user_id = get_current_user_id()
                if user_id:
                    user = db.users.find_one({"_id": ObjectId(user_id)})
                    if user and "prompts" in user:
                        prompts = db.prompts.find_one({"_id": user["prompts"]})
                        if prompts:
                            config_key = f"{self.search_provider_type}_config"
                            if config_key in prompts and prompts[config_key]:
                                user_config = prompts[config_key]
            except Exception as e:
                print(f"Error al obtener la configuración del usuario: {str(e)}")
            
            # Extraer la keyword con Groq
            system_prompt = get_keyword_extraction_prompt()

            keyword_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
            )
            content_str = keyword_response.choices[0].message.content or ""

            # Extraer el JSON de la respuesta usando regex - puede contener texto antes o después
            try:
                # Buscar un objeto JSON válido en la cadena
                json_match = re.search(r"\{[\s\S]*?\}", content_str)
                if json_match:
                    json_str = json_match.group(0)
                    keyword_json = json.loads(json_str)
                    keyword = keyword_json.get("keyword", query)
                else:
                    print(f"No se encontró un objeto JSON válido en: {content_str}")
                    keyword = query
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error decodificando JSON de respuesta keyword: {content_str}")
                print(f"Error detallado: {str(e)}")
                keyword = query

            # Determinar el tipo de proveedor para buscar en la caché
            provider_cache_type = "tavily_search" if isinstance(self.search_provider, TavilyProvider) else "serpapi_search"
            
            # Verificar caché para la keyword específica
            keyword_cache_key = CacheManager.generate_cache_key(
                keyword, provider_cache_type
            )
            cached_search = CacheManager.get_from_cache(keyword_cache_key)

            # Verificar si hay resultados en caché o si debemos realizar la búsqueda
            if cached_search:
                search_results = cached_search
                print(f"Resultado de búsqueda recuperado de caché para keyword: {keyword}")
            else:
                # Realizar búsqueda con el proveedor configurado y la configuración del usuario
                search_results = self.search_provider.search(keyword, user_config)
                
                # Guardar resultados de búsqueda en caché
                if search_results and "error" not in search_results:
                    CacheManager.save_to_cache(
                        cache_key=keyword_cache_key,
                        response=search_results,
                        provider_type=provider_cache_type,
                        query=keyword,
                    )

            # Verificar si hay resultados
            if not search_results or "error" in search_results:
                error_msg = (
                    search_results.get("error", "Error desconocido en la búsqueda")
                    if search_results
                    else "No se obtuvieron resultados de búsqueda"
                )
                print(f"Error en búsqueda {provider_cache_type}: {error_msg}")
                return {"error": error_msg, "success": False}

            # Procesar los resultados según el tipo de proveedor
            if isinstance(self.search_provider, TavilyProvider):
                content_to_process = self._process_tavily_results(search_results)
            else:
                content_to_process = self._process_search_results(search_results)

            if not content_to_process:
                return {
                    "error": "No se encontraron resultados relevantes",
                    "success": False,
                }

            # Obtener el prompt personalizado del usuario para procesar resultados
            custom_prompt = None
            try:
                if user_id:
                    user = db.users.find_one({"_id": ObjectId(user_id)})
                    if user and "prompts" in user:
                        prompts = db.prompts.find_one({"_id": user["prompts"]})
                        if prompts:
                            prompt_key = f"{self.search_provider_type}_prompt"
                            if prompt_key in prompts and prompts[prompt_key]:
                                custom_prompt = prompts[prompt_key]
            except Exception as e:
                print(f"Error al obtener el prompt personalizado: {str(e)}")
            
            # Usar el prompt personalizado o el predeterminado
            from api.serviceAi.prompts import get_web_search_prompt
            language = "es"  # Valor predeterminado
            try:
                if user_id:
                    user = db.users.find_one({"_id": ObjectId(user_id)})
                    if user:
                        language = user.get("language", "es")
            except Exception:
                pass
                
            system_content = custom_prompt or get_web_search_prompt(language)
            system_content = f"{system_content}\n\nResultados de búsqueda:\n{content_to_process}"

            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": query},
                ],
            )

            result = {
                "content": final_response.choices[0].message.content,
                "success": True,
                "search_results": search_results,
            }

            # Guardar resultado final en caché
            CacheManager.save_to_cache(
                cache_key=cache_key,
                response=result,
                provider_type="groq_web_search",
                query=query,
            )

            return result

        except Exception as e:
            print(f"Error en búsqueda web con Groq y {self.search_provider_type}: {str(e)}")
            # Si falla la búsqueda, intentamos la simulación
            return self._simulate_web_search(query)

    def _simulate_web_search(self, query: str) -> Dict[str, Any]:
        """
        Método de respaldo que simula una búsqueda web cuando SerpAPI no está disponible.

        Args:
            query: La consulta de búsqueda

        Returns:
            Resultados simulados de la búsqueda
        """
        # Verificar caché primero
        cache_key = CacheManager.generate_cache_key(query, "groq_simulate_search")
        cached_result = CacheManager.get_from_cache(cache_key)
        if cached_result:
            print(f"Resultado simulado recuperado de caché para: {query}")
            return cached_result

        try:
            system_prompt = get_web_search_prompt()

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Búsqueda web: {query}"},
                ],
            )

            result = {"content": response.choices[0].message.content, "success": True}

            # Guardar en caché
            CacheManager.save_to_cache(
                cache_key=cache_key,
                response=result,
                provider_type="groq_simulate_search",
                query=query,
            )

            return result

        except Exception as e:
            print(f"Error en búsqueda simulada con Groq: {str(e)}")
            return {"error": str(e), "success": False}
