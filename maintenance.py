"""
Script de mantenimiento para UpdateMe que se encarga de enviar
los correos semanales a los usuarios.

Este script debe ejecutarse periódicamente (una vez al día o más) para
garantizar que todos los usuarios reciban su resumen semanal.
"""

#!/usr/bin/env python3


import os
import time
import logging
import sys
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
from api.services import generate_news_summary, send_email

# Configuración de logging
# Verificar si estamos en Vercel (entorno de producción)
if os.environ.get("VERCEL") == "1":
    # En Vercel, solo usar StreamHandler para evitar errores de escritura en filesystem
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
else:
    # En entorno local, usar FileHandler y StreamHandler
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("email_sender.log"), logging.StreamHandler()],
    )

logger = logging.getLogger("email_sender")

# Cargar variables de entorno
load_dotenv()

# Conectar a la base de datos
MONGODB_URI = os.environ.get("MONGODB_URI")

client = MongoClient(MONGODB_URI)
db = client["updateme"]
users_collection = db["users"]


def send_weekly_email(user: dict) -> bool:
    """Envía un correo electrónico con el resumen semanal de noticias para un usuario específico.

    Args:
        user (dict): Diccionario que contiene la información del usuario, incluyendo su correo electrónico y preferencias.

    Returns:
        bool: True si el correo se envió correctamente, False en caso contrario.
    """
    try:
        email = user["email"]
        language = user.get("language", "es")
        provider = user.get("ai_provider", "groq")

        # Generar el resumen personalizado para el usuario
        logger.info(f"Generando resumen para {email} usando proveedor {provider}")
        summary_content = generate_news_summary(email, provider)

        # Determinar el asunto según el idioma
        subject = (
            "Your Weekly Tech Update - UpdateMe"
            if language == "en"
            else "UpdateMe: Tu resumen semanal de tecnología e IA"
        )

        # Enviar el correo
        logger.info(f"Enviando correo a {email}")
        send_email(email, subject, summary_content)

        # Actualizar la fecha del último correo enviado
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_email_sent": datetime.now(timezone.utc)}},
        )

        logger.info(f"Correo enviado exitosamente a {email}")
        return True

    except Exception as e:
        logger.error(f"Error enviando correo a {user['email']}: {str(e)}")
        return False


def process_pending_emails(days_interval: int = 6) -> tuple:
    """Procesa los correos pendientes de los usuarios, enviándolos si es necesario.
    Si no hay correos pendientes, no hace nada.

    Por defecto son 6 ya que el mensaje puede tardar en enviarse, haciendo que el usuario tarde más de 7 días en recibirlo.

    Args:
        days_interval (int, optional): Número de días para considerar un correo como pendiente. Defaults to 6.

    Returns:
        tuple: Contiene el número total de usuarios procesados, el número de correos enviados exitosamente y el número de errores.
    """
    # Calcular la fecha límite (ahora - intervalo de días)
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_interval)

    # Buscar usuarios que no han recibido un correo en el intervalo especificado
    # o que nunca han recibido un correo (last_email_sent es null)
    query = {
        "$or": [{"last_email_sent": {"$lt": cutoff_date}}, {"last_email_sent": None}],
        "account_status": "active",  # Solo usuarios activos
    }

    # Obtener la lista de usuarios que necesitan recibir correo
    users_to_process = list(users_collection.find(query))
    total_users = len(users_to_process)

    logger.info(f"Se encontraron {total_users} usuarios para procesar")

    success_count = 0
    error_count = 0

    # Procesar cada usuario
    for user in users_to_process:
        try:
            # Añadir un pequeño retraso para evitar sobrecargar el sistema
            time.sleep(1)

            result = send_weekly_email(user)
            if result:
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            logger.error(f"Error procesando usuario {user['email']}: {str(e)}")
            error_count += 1

    return total_users, success_count, error_count


if __name__ == "__main__":
    logger.info("Iniciando proceso de envío de correos semanales")

    try:
        total, success, errors = process_pending_emails()

        logger.info(f"Proceso completado: {total} usuarios procesados")
        logger.info(f"Éxitos: {success}, Errores: {errors}")

    except Exception as e:
        logger.error(f"Error en el proceso principal: {str(e)}")

    finally:
        # Cerrar la conexión a MongoDB
        client.close()
        logger.info("Conexión a MongoDB cerrada")
