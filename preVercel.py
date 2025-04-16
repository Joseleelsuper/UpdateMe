"""
Script de pre-inicialización para Vercel - compila las traducciones durante el arranque
"""
import os
import subprocess

def compile_translations():
    """
    Compila los archivos de traducción (.po) a archivos binarios (.mo)
    """
    try:
        # Obtener el directorio raíz del proyecto
        root_dir = os.path.dirname(os.path.abspath(__file__))
        translations_path = os.path.join(root_dir, "translations")
        
        print(f"Compilando traducciones en: {translations_path}")
        print(f"Contenido del directorio: {os.listdir(translations_path)}")
        
        # Ejecutar el comando pybabel
        compile_cmd = f"pybabel compile -d {translations_path}"
        result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
        
        print(f"Comando ejecutado: {compile_cmd}")
        print(f"Resultado de compilación: {result.stdout}")
        
        if result.stderr:
            print(f"Errores: {result.stderr}")
            
        # Verificar que se hayan creado los archivos .mo
        for lang in os.listdir(translations_path):
            lang_path = os.path.join(translations_path, lang, "LC_MESSAGES")
            if os.path.exists(lang_path):
                print(f"Archivos en {lang_path}: {os.listdir(lang_path)}")
                
        return True
    except Exception as e:
        print(f"Error al compilar traducciones: {e}")
        return False

# Ejecutar la compilación si este script es ejecutado directamente
if __name__ == "__main__":
    compile_translations()