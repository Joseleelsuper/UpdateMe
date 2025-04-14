import sys
import os

# Añadir el directorio raíz al path para poder importar app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as application

# Para Vercel
app = application

# Esto permite que Vercel importe la aplicación correctamente
