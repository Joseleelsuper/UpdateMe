"""
Implementación de DeepSeek como proveedor de IA.
"""

import json
from typing import Dict, Any
from openai import OpenAI

from .base_provider import BaseAIProvider
from .serpapi_provider import SerpAPIProvider
from .talivy_provider import TavilyProvider
from .prompts import get_keyword_extraction_prompt
from ..cache_manager import CacheManager


class DeepSeekProvider(BaseAIProvider):
    """
    Implementación del proveedor de IA DeepSeek.
    """

    def __init__(self, api_key: str, **kwargs):
        """
        Inicializa el proveedor de IA DeepSeek.

        Args:
            api_key: La clave API de DeepSeek
            kwargs: Parámetros adicionales como modelo y clave API de búsqueda
        """
        super().__init__(api_key, **kwargs)
        self.model = kwargs.get("model", "deepseek-chat")

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

        # Inicializar cliente de DeepSeek
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com",
        )

    def generate_content(self, prompt: str, **kwargs) -> str:
        """
        Genera contenido utilizando la API de DeepSeek.

        Args:
            prompt: El prompt para generar contenido
            kwargs: Parámetros adicionales como temperatura

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
                prompt, "deepseek_content", cache_params
            )
            cached_content = CacheManager.get_from_cache(cache_key)

            if cached_content:
                print("Contenido recuperado de caché para prompt similar")
                return str(cached_content)

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
                provider_type="deepseek_content",
                query=prompt,
            )

            return result
        except Exception as e:
            print(f"Error generando contenido con DeepSeek: {str(e)}")
            return f"Error: {str(e)}"

    def search_web(self, query: str) -> Dict[str, Any]:
        """
        Realiza una búsqueda web utilizando el proveedor configurado y procesa los resultados con DeepSeek.

        Args:
            query: La consulta de búsqueda

        Returns:
            Resultados procesados de la búsqueda
        """
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
        
        if not self.search_provider:
            return {
                "error": "No se ha configurado un proveedor de búsqueda",
                "success": False,
            }

        # Verificar caché primero
        cache_key = CacheManager.generate_cache_key(query, "deepseek_web_search")
        cached_result = CacheManager.get_from_cache(cache_key)
        if cached_result:
            print(f"Resultado recuperado de caché para: {query}")
            return cached_result

        try:
            # Primero obtenemos la keyword mediante DeepSeek
            system_prompt = get_keyword_extraction_prompt()

            keyword_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
                response_format={"type": "json_object"},
            )

            # Extraer la keyword del JSON
            content_str = keyword_response.choices[0].message.content or "{}"
            try:
                keyword_json = json.loads(content_str)
                keyword = keyword_json.get("keyword", query)
            except json.JSONDecodeError:
                print(f"Error decodificando JSON de respuesta keyword: {content_str}")
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
                print(
                    f"Resultado de búsqueda recuperado de caché para keyword: {keyword}"
                )
            else:
                # Realizar búsqueda con el proveedor configurado
                search_results = self.search_provider.search(keyword)
                
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

            # Procesar los resultados con DeepSeek
            system_content = f"Answer the question from user with the provided search information: {content_to_process}"

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
                provider_type="deepseek_web_search",
                query=query,
            )

            return result

        except Exception as e:
            print(f"Error en búsqueda web con DeepSeek y {self.search_provider_type}: {str(e)}")
            return {"error": str(e), "success": False}
