"""
Permite ejecutar todas las pruebas en un directorio de tests para probar el funcionamiento correcto del proyecto.
"""

import unittest
import sys

# Descubre y ejecuta todas las pruebas en el directorio tests/
loader = unittest.TestLoader()
start_dir = "tests"
suite = loader.discover(start_dir)

runner = unittest.TextTestRunner()
result = runner.run(suite)

# Salir con código de error si alguna prueba falló
sys.exit(not result.wasSuccessful())
