# run_local.py
import json
import sys
from app.services.file_processing import process_document
from app.services.ai_handler import analyze_document_with_ai

# --- CONFIGURACIÓN DE PRUEBA ---
# Coloca la ruta a tu CV (PDF o Imagen)
TEST_FILE_PATH = "/home/olguin/Downloads/CV_AlejandroOlguin_EspecialistaIA.pdf" 
#TEST_FILE_PATH = "/home/olguin/Downloads/CI-AlejandroOlguin.pdf"
#TEST_FILE_PATH = "/home/olguin/Documents/CV-Ejemplos/AlejandroNunezArroyo.pdf"
# ------------------------------

def main():
    """Ejecuta el pipeline de análisis de documentos completo."""
    print("--- INICIANDO ANÁLISIS DEL DOCUMENTO ---")
    print(f"Documento a analizar: {TEST_FILE_PATH}")
    
    # 1. ETAPA B: Procesamiento de archivos (Los Ojos)
    base64_content = process_document(TEST_FILE_PATH)
    
    if not base64_content:
        print("Análisis detenido. No se pudo procesar el archivo.")
        sys.exit(1)
        
    print(f"  -> Archivo procesado exitosamente (longitud: {len(base64_content)} bytes en Base64).")

    # 2. ETAPA C: Llamada a la IA (El Cerebro)
    # Aquí es donde se llama a la API de gpt-5-mini
    analysis_result = analyze_document_with_ai(base64_content)

    if analysis_result:
        print("\n--- RESULTADO DE LA EXTRACCIÓN (JSON) ---")
        # Imprime el resultado con formato bonito
        print(json.dumps(analysis_result, indent=4, ensure_ascii=False))
        
        # Muestra el resumen (Requisito 4)
        print("\n--- RESUMEN DEL DOCUMENTO ---")
        print(analysis_result.get('resumen'))
    else:
        print("\n--- FALLO DEL ANÁLISIS ---")
        print("La IA no pudo generar un resultado válido o hubo un error de conexión.")


if __name__ == "__main__":
    main()