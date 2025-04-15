"""
Este archivo maneja la configuración de la base de datos MongoDB.
"""
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración MongoDB
MONGODB_URI = os.environ.get("MONGODB_URI")
client = MongoClient(MONGODB_URI, server_api=ServerApi("1"))
db = client["updateme"]
users_collection = db["users"]