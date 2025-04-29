"""
Archivo de compatibilidad que importa la aplicación desde el módulo api.
Este archivo mantiene retrocompatibilidad con el código existente.
"""

import os
from api.index import app

if __name__ == "__main__":
    os.system("pybabel compile -d translations")
    app.run(debug=True)
