#!/usr/bin/env python3

"""
Script de mantenimiento para UpdateMe que se encarga de enviar
los correos semanales a los usuarios.

Este script debe ejecutarse periódicamente (una vez al día o más) para
garantizar que todos los usuarios reciban su resumen semanal.
"""

import os
import time
import logging
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
from api.services import generate_news_summary, send_email

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s',
    handlers=[
        logging.FileHandler("email_sender.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("email_sender")

# Cargar variables de entorno
load_dotenv()

# Conectar a la base de datos
MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME", "updatemeprod")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
users_collection = db["users"]

def send_weekly_email(user):
    """
    Envía el correo semanal a un usuario específico.
    
    Args:
        user: Documento de usuario de la base de datos
        
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    try:
        email = user["email"]
        language = user.get("language", "es")
        provider = user.get("ai_provider", "groq")
        
        # Generar el resumen personalizado para el usuario
        logger.info(f"Generando resumen para {email} usando proveedor {provider}")
        summary_content = generate_news_summary(email, provider)
        
        # Determinar el asunto según el idioma
        subject = "Your Weekly Tech Update - UpdateMe" if language == "en" else "UpdateMe: Tu resumen semanal de tecnología e IA"
        
        # Enviar el correo
        logger.info(f"Enviando correo a {email}")
        send_email(email, subject, summary_content)
        
        # Actualizar la fecha del último correo enviado
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_email_sent": datetime.now(timezone.utc)}}
        )
        
        logger.info(f"Correo enviado exitosamente a {email}")
        return True
        
    except Exception as e:
        logger.error(f"Error enviando correo a {user['email']}: {str(e)}")
        return False

def process_pending_emails(days_interval=7):
    """
    Procesa todos los usuarios que necesitan recibir su correo semanal.
    
    Args:
        days_interval: Número de días entre envíos (por defecto 7 días)
    
    Returns:
        tuple: (total_users, success_count, error_count)
    """
    # Calcular la fecha límite (ahora - intervalo de días)
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_interval)
    
    # Buscar usuarios que no han recibido un correo en el intervalo especificado
    # o que nunca han recibido un correo (last_email_sent es null)
    query = {
        "$or": [
            {"last_email_sent": {"$lt": cutoff_date}},
            {"last_email_sent": None}
        ],
        "account_status": "active"  # Solo usuarios activos
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
