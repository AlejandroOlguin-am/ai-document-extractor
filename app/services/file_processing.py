import base64
import os
from io import BytesIO
from typing import Optional

# Librerías de la Etapa B
from PIL import Image
from pdf2image import convert_from_path, exceptions as pdf_exceptions

# --------------------------------------------------------------------------
# 1. FUNCIONES AUXILIARES
# --------------------------------------------------------------------------

def _convert_pil_to_base64(img: Image.Image) -> str:
    """Convierte un objeto de imagen PIL a una cadena Base64."""
    try:
        # Guardamos la imagen en un buffer de memoria como JPEG
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        # Codificamos el contenido del buffer a Base64
        base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return base64_image
    except Exception as e:
        print(f"Error al codificar imagen a Base64: {e}")
        raise

# --------------------------------------------------------------------------
# 2. MANEJO DE ARCHIVOS ESPECÍFICOS
# --------------------------------------------------------------------------

def _process_pdf_file(file_path: str) -> Optional[str]:
    """Convierte la primera página de un PDF a Base64."""
    print(f"  -> Procesando PDF: {file_path}")
    try:
        # Convertimos solo la primera página (first_page=1, last_page=1)
        # Esto reduce el tiempo y el costo de la API.
        images = convert_from_path(file_path, first_page=1, last_page=1, dpi=200)
        if images:
            # Usamos la función auxiliar para codificar la imagen
            return _convert_pil_to_base64(images[0])
        return None
    except pdf_exceptions.PDFPageCountError:
        print("Error: El archivo PDF está vacío.")
        return None
    except Exception as e:
        print(f"Error específico de Poppler o PDF: {e}")
        return None

def _process_image_file(file_path: str) -> Optional[str]:
    """Convierte una imagen (JPG/PNG) a Base64."""
    print(f"  -> Procesando Imagen: {file_path}")
    try:
        img = Image.open(file_path)
        return _convert_pil_to_base64(img)
    except Exception as e:
        print(f"Error al abrir o codificar la imagen: {e}")
        return None

# --------------------------------------------------------------------------
# 3. FUNCIÓN PRINCIPAL
# --------------------------------------------------------------------------

def process_document(file_path: str) -> Optional[str]:
    """
    Función principal para procesar un documento (PDF o Imagen) 
    y retornar su contenido codificado en Base64.
    """
    if not os.path.exists(file_path):
        print(f"Error: Archivo no encontrado en la ruta: {file_path}")
        return None

    # Obtenemos la extensión del archivo en minúsculas
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension in ['.pdf']:
        return _process_pdf_file(file_path)
    elif file_extension in ['.jpg', '.jpeg', '.png']:
        return _process_image_file(file_path)
    else:
        print(f"Error: Formato de archivo '{file_extension}' no soportado.")
        return None