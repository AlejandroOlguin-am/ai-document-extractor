# app/services/ai_handler.py
import json
from typing import Optional
from openai import OpenAI
from pydantic import ValidationError

from app.core.config import settings
from app.models.schemas import RespuestaAnalisis 

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def analyze_document_content(content: str, filename: str, is_image_mode: bool = False) -> dict:
    """
    Analiza el documento. 
    - Si is_image_mode=True, 'content' es Base64.
    - Si is_image_mode=False, 'content' es Texto plano.
    """
    print(f"  -> Llamando al Agente IA (Modo: {'VISION' if is_image_mode else 'TEXTO'})...")

    schema_str = json.dumps(RespuestaAnalisis.model_json_schema(), indent=2)

    SYSTEM_PROMPT_TEXT = f"""
    Eres un motor de extracción de datos para RRHH. Tu entrada será el NOMBRE DEL ARCHIVO y el TEXTO CRUDO extraído de un documento.
    Tu objetivo es CLASIFICAR el documento y ESTRUCTURAR la información en JSON estricto.

    ### REGLAS DE CLASIFICACIÓN Y EXTRACCIÓN:

    1. **PRIORIDAD CV (Currículum Vitae):**
    - Si el texto contiene secciones como "Experiencia", "Educación", "Habilidades", "Perfil", o fechas laborales, clasifícalo como 'CV'.
    2. **Extracción y Mapeo:** Busca los siguientes datos y mápelos a los campos EXACTOS de salida:
    - **Mapeo a `nombre`:** Busca en encabezados, firmas o secciones "Datos Personales".
    - **Mapeo a `email`:** Busca cualquier dirección de correo electrónico en el texto.
    - **Mapeo a `telefono`:** Busca números de teléfono con formatos comunes (con o sin código de país).
    - **Mapeo a `educacion_principal`:** Busca en secciones con título "Educación", "Formación" o "Estudios".
    - **Mapeo a `habilidades_clave`:** Busca en secciones con título "Skills", "Competencias" o "Destrezas".
    - **Mapeo a `ultima_experiencia`:** Identifica la última entrada cronológica en la sección "Experiencia Profesional" o "Historial Laboral".
    - **Mapeo a `resumen`:** Busca en secciones con título "Perfil", "Acerca de Mí", "Objetivo", "Summary", o "Statement".
            - SI NO EXISTE: GÉNERALO tú mismo basándote en la experiencia y habilidades leídas.
            - **ONE-SHOT (Ejemplo de estilo de Resumen):** "Perfil tecnológico con sólidos conocimientos en desarrollo Backend y Python, con experiencia en liderazgo de equipos y fuerte interés en Inteligencia Artificial.".
    
    3. **Tolerancia a la Extracción:** Si no encuentra un campo con el nombre exacto del esquema, DEBE buscar el sinónimo antes de rendirse.
    
    4. **PRIORIDAD CI (Cédula de Identidad/DNI):**
    - Si no parece CV, busca palabras clave: "Cédula de Identidad", "Estado Plurinacional de Bolivia", "Serie", "Sección", "Fecha de Nacimiento" junto a un número de identificación.
    - Clasifícalo como 'CI'.
    - **Extracción:** Busca Nombre Completo, Número de Documento (limpia el número de letras o errores de OCR), Fecha Nacimiento.

    5. **NO IDENTIFICADO:**
    - Si el texto es ilegible, incoherente o no corresponde a lo anterior, clasifica como 'NO_IDENTIFICADO'.
    - Todos los campos de datos deben ser `null`.
    - El resumen debe decir: "Documento no reconocido como CV o CI válido."

    ### FORMATO DE SALIDA (ESTRICTO):
    Debes responder ÚNICAMENTE con un JSON válido que cumpla este esquema:
    {schema_str}
    """

    SYSTEM_PROMPT_VISION = f"""
    Eres un Agente de Visión Artificial experto en Procesamiento Inteligente de Documentos (IDP) para RRHH.
    Tu entrada es una imagen (foto, escaneo o PDF renderizado) y tu objetivo es CLASIFICAR, EXTRAER y VALIDAR datos con precisión forense.

    ### FASE 0: EVALUACIÓN DE CALIDAD Y SALIDA ANTICIPADA

    1. **CRITERIOS DE FALLO:** Antes de cualquier extracción, evalúa si la imagen cae en alguna de estas categorías:
    a. **Muy Baja Resolución o Borrosa:** El texto clave (nombres, números) no es legible para un humano.
    b. **Exceso de Ruido Visual:** Demasiadas sombras, brillo, o la imagen está cortada de forma incompleta.
    c. **Imagen Irrelevante:** Fotos de objetos, personas, mascotas, paisajes, etc.

    2. **FALLO:** Si la imagen cumple alguno de los criterios de fallo, DEBES DEVOLVER ESTE JSON ESPECÍFICO e ignorar las Fases 1 y 2:
    - tipo_documento: "NO_IDENTIFICADO"
    - resumen: "Documento/imagen no relacionada o de muy baja calidad."
    - datos_cv: null
    - datos_ci: null

    ### FASE 1: ATENCIÓN VISUAL Y "RECORTE MENTAL"
    Antes de leer texto, analiza la composición de la imagen:
    1. **Detección de Objetos:** ¿Ves tarjetas de identificación (Cédulas), dos lados (anverso/reverso)?
    2. **FILTRO DE RUIDO (CRÍTICO):** Ignora el fondo (bordes de hoja blanca, sombras). **Centra tu atención exclusivamente en el contenido textual dentro de los bordes de los cuadrantes.**

    ### FASE 2: LÓGICA DE CLASIFICACIÓN Y EXTRACCIÓN

    #### A. PRIORIDAD ALTA: CÉDULA DE IDENTIDAD (CI)
    Si detectas el formato visual de una Cédula (tarjeta con foto, escudo, título "Cédula de Identidad" o "Estado Plurinacional de Bolivia"):
    - **Clasificación:** 'CI'.
    - **Estrategia de Extracción (OCR con Chain-of-Thought):**
        1. **Nombre Completo:** Extrae apellidos y nombres.
        2. **Número de Documento (VALIDACIÓN ADAPTABLE):**
            - *Paso A (Localización):* Identifica el número del CI.
            - *Paso B (Recuento de lados):* Determina cuántos lados del CI son visibles (uno o dos).
            - *Paso C (Transcripción y CoT):* Transcribe el número encontrado dígito por dígito.
            - *Paso D (Validación):*
                - **SI SOLO SE VE UN LADO:** Procede con el número transcrito en el Paso C.
                - **SI SE VEN DOS LADOS (Anverso y Reverso):** Los números DEBEN COINCIDIR. Si no coinciden copia el que este mas claro o si la certeza es baja, DEJA el campo como `""` (cadena vacía) o `null`.
            - *Restricción Final:* El número debe ser una cadena limpia de 7 a 10 dígitos.
        3. **Fecha de Nacimiento:** Extrae este campo con exactitud.
        4. **Lugar de Emisión:** Solo si está presente, dejar `null` si no.
    - **Resumen (ONE-SHOT):** Genera un resumen solo con este formato: 
        *Ejemplo:* "Cédula de Identidad de Alejandro Olguin, ciudadano boliviano, nacido el 15/05/2000 (24 años)"

    #### B. PRIORIDAD MEDIA: CURRÍCULUM VITAE (CV)
    Si NO detectas un CI, analiza si la imagen es un documento de texto con secciones de "Experiencia", "Educación", etc.:
    - **Clasificación:** 'CV'.
    - **Extracción:** Aplica OCR visual para extraer Nombre, Email, Teléfono, Título, Última Experiencia y Skills.
    - **Resumen:** Segun la informacion del cv. 
            - **ONE-SHOT (Ejemplo de estilo de Resumen):** "Perfil tecnológico con sólidos conocimientos en desarrollo Backend y Python, con experiencia en liderazgo de equipos y fuerte interés en Inteligencia Artificial.".

    ### FORMATO DE SALIDA (ESTRICTO):
    Responde ÚNICAMENTE con el siguiente JSON válido (sin markdown):
    {schema_str}
    """
    user_content = []
    if is_image_mode:
        system_prompt = SYSTEM_PROMPT_VISION
        user_content = [
            {
                "type": "text", 
                "text": f"NOMBRE DEL ARCHIVO: '{filename}'\n\nINSTRUCCIÓN: Aplica el 'Recorte Mental' a la imagen adjunta. Si es un CI, verifica el número dígito por dígito (anverso/reverso). Genera el JSON estricto."
            },
            {"type": "image_url", "image_url": {
                "url": f"data:image/jpeg;base64,{content}"
            }}
        ]
    else:
        system_prompt = SYSTEM_PROMPT_TEXT
        user_content = [
            {"type": "text", "text": f"Analiza el siguiente texto:\n\n{content}, clasifica y extrae los datos en JSON. El nombre del archivo es: {filename}."}
        ]

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={
                "type": "json_object",
            }
        )
        
        raw_json = response.choices[0].message.content
        print(" -> Respuesta cruda de la IA recibida.")
        print( raw_json)
        print(" -> Validando y parseando el JSON con Pydantic...")

        data = json.loads(raw_json)

        validated_data = RespuestaAnalisis.model_validate(data)
        
        return validated_data.model_dump() 

    except ValidationError as e:
        print(f"Error de validación Pydantic: La IA generó un JSON inválido. Detalles: {e}")
        return 
    except Exception as e:
        print(f"Error en la llamada a la API de OpenAI: {e}")
        return 