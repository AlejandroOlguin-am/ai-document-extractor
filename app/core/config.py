# app/core/config.py
from dotenv import load_dotenv, find_dotenv
import os

env_path = find_dotenv()
if env_path:
    load_dotenv()

class Settings:
    # Si la clave no está en .env, dará error. Esto es intencional y bueno.
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY") 
    # Usaremos el modelo más capaz para esta tarea de visión y JSON
    OPENAI_MODEL: str = "gpt-5-mini" 
    # Opcionalmente, puedes probar con el "gpt-4o" si el nano no es lo suficientemente bueno para JSON

    if not OPENAI_API_KEY:
        raise ValueError("La variable de entorno OPENAI_API_KEY no está configurada.")
    
settings = Settings()