# main.py
import uvicorn
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from starlette.responses import JSONResponse
from typing import Dict, Any

# Importamos nuestros servicios y modelos
from app.services.file_processing import process_document
from app.services.ai_handler import analyze_document_with_ai

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="AI Document Analyzer",
    description="API para clasificar, extraer y resumir documentos (CV/CI) usando modelos GPT-5.",
    version="1.0.0"
)

# ----------------------------------------------------------------------
# ENDPOINT PRINCIPAL: POST /analyze
# ----------------------------------------------------------------------

@app.post("/analyze", response_model=Dict[str, Any])
async def analyze_document_endpoint(
    document: UploadFile = File(..., description="Archivo a analizar (PDF, JPG, o PNG).")
):
    """
    Recibe un documento y devuelve el análisis JSON de la IA.
    """
    
    # --- 1. Guardar el archivo temporalmente ---
    # FastAPI solo da acceso a los bytes. Lo guardamos en disco para
    # que pdf2image y PIL puedan acceder a él por ruta, como en la prueba local.
    
    # Usamos un archivo temporal seguro
    with tempfile.NamedTemporaryFile(delete=False, suffix=document.filename) as tmp:
        # Copiamos el contenido del archivo subido al archivo temporal
        shutil.copyfileobj(document.file, tmp)
        temp_file_path = tmp.name
        
    try:
        # --- 2. ETAPA B: Procesamiento del archivo (Base64) ---
        print(f"[{document.filename}] -> Iniciando procesamiento de archivo...")
        base64_content = process_document(temp_file_path)

        if not base64_content:
            raise HTTPException(status_code=422, detail="Formato de archivo no soportado o archivo vacío.")
            
        # --- 3. ETAPA C: Llamada a la IA ---
        print(f"[{document.filename}] -> Llamando al Agente IA...")
        analysis_result = analyze_document_with_ai(base64_content)
        
        if not analysis_result:
            raise HTTPException(status_code=500, detail="La IA no pudo generar un JSON válido o la validación Pydantic falló.")

        # --- 4. Respuesta exitosa ---
        return JSONResponse(content=analysis_result)

    finally:
        # --- 5. Limpieza (IMPORTANTE) ---
        # Aseguramos que el archivo temporal sea eliminado, incluso si hay errores
        import os
        os.remove(temp_file_path)
        print(f"[{document.filename}] -> Limpieza de archivo temporal.")


if __name__ == "__main__":
    # Comando para iniciar el servidor
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)