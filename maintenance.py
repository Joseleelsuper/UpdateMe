"""
Script de mantenimiento para tareas periódicas como limpiar la caché.
Este script puede ejecutarse mediante un cron job o tarea programada.
"""
import os
import sys
from dotenv import load_dotenv

from api.cache_manager import CacheManager

# Añadir el directorio raíz al path para permitir importaciones
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

# Cargar variables de entorno
load_dotenv()


def clean_cache():
    """Limpia las entradas de caché antiguas."""
    days_to_keep = 7  # Mantener una semana de caché
    deleted_count = CacheManager.clear_expired_cache(days_to_keep)
    print(f"Se eliminaron {deleted_count} entradas de caché antiguas.")

if __name__ == "__main__":
    clean_cache()
