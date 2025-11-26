# 🤖 AI Document Processor (IDP) - Agente de Clasificación y Extracción

## 1. Descripción del Proyecto

Este proyecto es una API RESTful construida con FastAPI que implementa un Agente de Procesamiento de Documentos Inteligente (IDP). Su función principal es clasificar y extraer datos estructurados de documentos de Recursos Humanos, como Currículums Vitae (CV) y Cédulas de Identidad (CI/DNI), utilizando técnicas de Prompt Engineering y modelos de lenguaje de gran escala (gpt-5-mini).

El objetivo es automatizar la ingesta de documentos, mapeando campos clave a una estructura JSON unificada, independientemente del formato de entrada (PDF, imagen escaneada o foto).

## 2. Arquitectura de Solución: Modo Híbrido

La aplicación opera bajo un Modo Híbrido de Análisis para maximizar la velocidad y la precisión, adaptándose dinámicamente al tipo de documento y la calidad de entrada.  [(Ver Diagrama de Flujo)](assets/arquitectura.png)

### A. Lógica de Agentes

| Modo de Entrada | Pipeline de Procesamiento | Propósito |
|---|---|---|
| TEXTO (PDF con texto nativo, alta coherencia) | PDF -> PyMuPDF (Extracción de Texto) | Velocidad y Economía. Utiliza el texto extraído para una extracción limpia de CV. |
| VISIÓN (Imagen, PDF escaneado, baja coherencia) | Imagen -> Conversión Base64 -> GPT-5 Vision | Precisión y Fiabilidad. Activa el modo multimodal para la extracción de CI y CVs difíciles. |

### B. Técnicas de Prompt Engineering Avanzado

Se utilizan técnicas de ingeniería de prompts avanzadas para garantizar la fiabilidad del agente:
- Chain-of-Thought (CoT): Se fuerza al modelo a razonar paso a paso, especialmente en la validación del número de CI (verificando coincidencia entre anverso y reverso).
- Recorte Cognitivo (Visual Grounding): Se instruye al modelo de visión a ignorar el ruido (sombras, fondos de mesa) y a centrar su atención solo en los bordes de la tarjeta o documento.
- Cribado de Calidad (Quality Screening): Implementación de una "puerta de salida anticipada" en el prompt para devolver NULL y un mensaje de error si la imagen es de muy baja calidad, borrosa o incoherente, protegiendo la fiabilidad de la base de datos.
- Tolerancia Semántica: El prompt de texto busca sinónimos para los títulos de CV (ej. "Perfil", "Acerca de Mí" para mapear a resumen), evitando fallos por rigidez léxica.

## 3. Tecnologías Utilizadas

- Backend: FastAPI
- Lenguaje: Python 3.10+
- Modelos LLM: GPT-5 (mini)
- Manejo de Archivos: pdf2image, Pillow (PIL)
- Configuración: python-dotenv para gestión de secretos (.env)
- Servidor Web: uvicorn

### 4. Instalación Local

Siga estos pasos para configurar y ejecutar el proyecto localmente.

**Requisitos:**

- Python 3.10 o superior
- libpoppler-dev (necesario para pdf2image en sistemas Linux/WSL. En macOS y Windows, la dependencia se resuelve automáticamente).

**Pasos:**

Clonar el Repositorio:

git clone [https://docs.github.com/es/repositories/creating-and-managing-repositories/quickstart-for-repositories](https://github.com/AlejandroOlguin-am/ai-document-extractor.git)  
cd ai-document-processor

Crear y Activar el Entorno Virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Linux/macOS
# venv\Scripts\activate  # En Windows
```

Instalar Dependencias:

```bash
pip install -r requirements.txt
```

Crear el Archivo de Entorno (.env):  
En la raíz del proyecto, cree un archivo llamado .env y agregue su clave de API. Este archivo está incluido en .gitignore por seguridad.

```env
# .env
OPENAI_API_KEY="sk-tu-clave-secreta-aqui"
```

## 5. Ejecución del Servidor

Ejecute el servidor FastAPI usando Uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en http://127.0.0.1:8000.

## 6. Uso de la API (Endpoint)

Documentación (Swagger UI)

Acceda a la interfaz interactiva de la API para probar el endpoint:  
👉 http://127.0.0.1:8000/docs

Endpoint Único de Análisis

Método: POST  
Endpoint: /analyze  
Descripción: Procesa un archivo subido (CV, CI, PDF o Imagen) y devuelve un JSON estructurado.  
Parámetros de request: file: (Requerido) El archivo a subir.

Ejemplo de Respuesta JSON (Éxito - CI):

```json
{
  "tipo_documento": "CI",
  "resumen": "Cédula de Identidad de Alejandro Olguin, ciudadano boliviano, nacido el 15/05/2000 (24 años).",
  "datos_cv": null,
  "datos_ci": {
    "nombre_completo": "Alejandro Olguin",
    "numero_documento": "12345678",
    "fecha_nacimiento": "2000-05-15",
    "lugar_emision": "Chuquisaca"
  }
}
```
## 7. Despliegue en Producción (Google Cloud Run)

Este proyecto está contenerizado y optimizado para entornos Serverless.

**Dockerización**

El proyecto incluye un Dockerfile configurado para producción, utilizando gunicorn como servidor de aplicaciones y uvicorn para los workers asíncronos.

**Despliegue Manual (GCP)**

El servicio puede ser desplegado en Google Cloud Run con los siguientes comandos:

  1. Construir Imagen:

  `gcloud builds submit --tag us-central1-docker.pkg.dev/[PROJECT_ID]/[REPO]/api-idp:latest`


  2. Desplegar Servicio:

  ```gcloud run deploy servicio-idp-datec \
      --image us-central1-docker.pkg.dev/[PROJECT_ID]/[REPO]/api-idp:latest \
      --region us-central1 \
      --platform managed \
      --allow-unauthenticated \
      --memory 1Gi \
      --timeout 300 \
      --set-env-vars OPENAI_API_KEY="[SECRET_KEY]"
  ```


URL de Producción Activa: [https://servicio-idp-datec-188177537900.us-central1.run.app/](https://servicio-idp-datec-188177537900.us-central1.run.app/docs#/)

*(Nota: La URL es pública para fines de demostración de este desafío técnico).*


***Desarrollado por [Alejandro Olguin](https://github.com/AlejandroOlguin-am)***