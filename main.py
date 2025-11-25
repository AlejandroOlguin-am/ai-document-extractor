# main.py (VERSIÓN FINAL CON MANEJO DE ERRORES)
import uvicorn
import shutil
import tempfile
import os # Necesitas importar os para la limpieza
from fastapi import FastAPI, UploadFile, File, HTTPException
from starlette.responses import JSONResponse
from typing import Dict, Any

# Importamos nuestros servicios y modelos
from app.services.file_processing import process_document
from app.services.ai_handler import analyze_document_content
from app.services.text_extraction import extract_text_from_pdf # Importar el nuevo servicio

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="DATEC AI Document Analyzer",
    description="API para clasificar, extraer y resumir documentos (CV/CI) usando modelos GPT-5 de DATEC.",
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
    file_name = document.filename
    # 1. Guardar el archivo temporalmente
    temp_file_path = None
    try:
        # Usamos un archivo temporal seguro
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_name) as tmp:
            shutil.copyfileobj(document.file, tmp)
            temp_file_path = tmp.name
        
        # --- LÓGICA DE PROCESAMIENTO ---
        ai_response = None
        
        # 1. Si es PDF, intentamos vía Rápida (Texto)
        if file_name.lower().endswith('.pdf'):
            print("-> Detectado PDF. Intentando extracción de texto rápida...")
            text_content = extract_text_from_pdf(temp_file_path)
            
            if text_content:
                print("-> Texto encontrado. Usando Modo Texto (Rápido).")
                # Llamamos a la IA con texto plano
                ai_response = analyze_document_content(text_content, file_name, is_image_mode=False)
        
        # 2. Si falló el texto o no es PDF, vamos por vía Lenta (Visión)
        if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')) and not ai_response:
            print("-> Usando Modo Visión (Fallback o Imagen nativa).")
            # Tu función process_document debe incluir la optimización de redimensionamiento
            base64_content = process_document(temp_file_path) 
            
            if base64_content:
                ai_response = analyze_document_content(base64_content, file_name, is_image_mode=True)

        # 3. Verificación Final de Éxito
        if not ai_response:
            # Si el archivo era soportado (no entró a HTTPException en la IA) 
            # pero la IA falló la validación o el contenido era irrelevante.
            raise HTTPException(
                status_code=400, 
                detail="No se pudo procesar el documento. Revise el formato o el contenido es ilegible/irrelevante."
            )
        
        # Respuesta exitosa
        return JSONResponse(content=ai_response)
        
    except HTTPException:
        # Re-lanza la excepción HTTP para que FastAPI la maneje
        raise
    except Exception as e:
        # Manejo de errores inesperados (ej. problemas de disco, errores internos de librerías)
        print(f"Error inesperado en el pipeline: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor durante el procesamiento.")

    finally:
        # --- LIMPIEZA GARANTIZADA ---
        # Este bloque SIEMPRE se ejecuta, incluso si hay un 'return' o un 'raise'
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"-> Limpieza de archivo temporal: {temp_file_path}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)