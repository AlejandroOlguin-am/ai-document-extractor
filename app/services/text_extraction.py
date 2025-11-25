# app/services/text_extraction.py
import fitz  # PyMuPDF

def extract_text_from_pdf(file_path: str) -> str:
    """
    Intenta extraer texto plano de un PDF.
    Retorna el texto si es suficiente, o cadena vacía si parece escaneado.
    """
    try:
        doc = fitz.open(file_path)
        text_content = ""
        
        # Leemos solo las primeras 2 páginas (suficiente para clasificar y extraer datos clave)
        for i, page in enumerate(doc):
            if i > 1: break 
            text_content += page.get_text() + "\n"
            
        # Heurística simple: Si hay muy poco texto, asumimos que es una imagen escaneada
        if len(text_content.strip()) < 50:
            return ""
            
        return text_content
    except Exception as e:
        print(f"Error extrayendo texto PDF: {e}")
        return ""