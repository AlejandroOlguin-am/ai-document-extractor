# app/services/ai_handler.py
import json
from typing import Optional
from openai import OpenAI
from pydantic import ValidationError

from app.core.config import settings
from app.models.schemas import RespuestaAnalisis # Importamos la salida definida

# Inicializar cliente de OpenAI (usa la clave cargada)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def analyze_document_with_ai(base64_image: str) -> Optional[dict]:
    """
    Envía la imagen Base64 a la API de OpenAI para clasificación, 
    extracción y resumen.
    """
    print("  -> Llamando al Agente IA...")

    schema_str = json.dumps(RespuestaAnalisis.model_json_schema(), indent=2)

    # El prompt definido previamente
    SYSTEM_PROMPT = f"""
    Eres un Agente de Ingeniería de Soluciones. Tu ÚNICA TAREA es generar un objeto JSON para el análisis de documentos (CV o CI).

    REGLAS CRÍTICAS DE OUTPUT:
    1. FORMATO: Tu respuesta DEBE ser un objeto JSON VÁLIDO. No incluyas explicaciones ni bloques de código (```json).
    2. ESQUEMA: Debes adherirte estrictamente a la estructura JSON definida a continuación. NO INVENTES CAMPOS NUEVOS, NO OMITAS CAMPOS REQUERIDOS.

    ESTRUCTURA DE DATOS A CUMPLIR:
    {schema_str}

    GUÍA DE CAMPO POR CAMPO:
    - tipo_documento: DEBE ser 'CV', 'CI' o 'NO_IDENTIFICADO'.
    - resumen: Campo REQUERIDO. Debe ser un resumen breve del contenido.
    - datos_cv/datos_ci: Debes llenar el sub-objeto correspondiente a tu clasificación (CV o CI) con los campos internos solicitados (ej: 'nombre_completo', 'habilidades_clave'). El campo NO utilizado DEBE ser null.
    - Campo de CV: Utiliza SIEMPRE 'nombre_completo', 'educacion_principal', 'ultima_experiencia' y 'habilidades_clave'. No uses 'nombre' o sub-objetos anidados.
    """

    try:
        # Usamos gpt-4o-mini por su capacidad de visión y manejo de JSON
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "text", "text": "Analiza el siguiente documento y genera el JSON."},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }}
                ]}
            ],
            # 💡 CLAVE: Forzamos la salida JSON usando el schema Pydantic
            response_format={
                "type": "json_object",
                # "schema": RespuestaAnalisis.model_json_schema()
            }
        )
        
        # Extraemos el texto JSON de la respuesta
        raw_json = response.choices[0].message.content
        print(" -> Respuesta cruda de la IA recibida.")
        print( raw_json)
        print(" -> Validando y parseando el JSON con Pydantic...")

        data = json.loads(raw_json)

        validated_data = RespuestaAnalisis.model_validate(data)
        
        return validated_data.model_dump() # Retornamos diccionario puro

    except ValidationError as e:
        print(f"Error de validación Pydantic: La IA generó un JSON inválido. Detalles: {e}")
        return None
    except Exception as e:
        # Aquí puedes manejar errores de la API (ej. clave inválida, archivo muy grande)
        print(f"Error en la llamada a la API de OpenAI: {e}")
        return None