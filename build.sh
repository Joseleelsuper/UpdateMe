#!/bin/bash
# Script para compilar traducciones en Vercel

echo "Instalando Babel..."
pip install babel flask-babel

echo "Compilando archivos de traducción..."
python -c "
import os
print('Directorio actual:', os.getcwd())
print('Listando archivos en translations:')
for root, dirs, files in os.walk('translations'):
    print(root, dirs, files)
"

# Compilar traducciones
pybabel compile -d translations

echo "Compilación de traducciones completada"