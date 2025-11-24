from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Union, Literal

# 1. Definición de Tipos de Documento para la clasificación (Requisito 2)
# Usamos Literal para restringir la respuesta de la IA a estos valores.
DocumentoTipo = Literal["CI", "CV", "NO_IDENTIFICADO"]

# 2. Esquemas de Extracción Específicos (Requisito 3)

class DatosCI(BaseModel):
    """Campos a extraer de una Cédula de Identidad."""
    nombre_completo: str = Field(..., description="Nombre completo de la persona.")
    numero_documento: str = Field(..., description="Número de Cédula de Identidad.")
    fecha_nacimiento: Optional[str] = Field(None, description="Fecha de nacimiento. Formato DD/MM/AAAA o similar.")
    lugar_emision: Optional[str] = Field(None, description="Lugar (Ciudad/Departamento) de emisión del documento.")

class DatosCV(BaseModel):
    """Campos a extraer de un Currículum Vitae."""
    nombre: str = Field(..., description="Nombre completo del postulante.")
    # Usamos EmailStr para validación de formato
    email: EmailStr = Field(..., description="Dirección de correo electrónico principal.")
    telefono: Optional[str] = Field(None, description="Número de teléfono de contacto.")
    educacion_principal: str = Field(..., description="Título de la educación superior más relevante (ej. 'Ingeniería Mecatrónica').")
    ultima_experiencia: str = Field(..., description="Resumen de la última experiencia o proyecto relevante.")
    habilidades_clave: list[str] = Field(..., description="Lista de 3 a 5 habilidades técnicas y blandas más relevantes.")

# 3. Modelo de Respuesta Final (Contenedor)

class RespuestaAnalisis(BaseModel):
    """Estructura de salida final que el Agente IA debe generar."""
    
    # Requisito 2: Clasificación
    tipo_documento: DocumentoTipo = Field(..., description="Clasificación del documento: 'CV', 'CI' o 'NO_IDENTIFICADO'.")
    
    # Requisito 4: Resumen
    resumen: str = Field(..., description="Resumen breve (máximo 4 líneas) del contenido del documento para una evaluación rápida. Debe permitir comprender el contenido sin revisar el documento completo.")
    
    # Requisito 3: Datos Extraídos (La IA solo debe llenar UNO de estos, basado en la clasificación)
    datos_cv: Optional[DatosCV] = Field(None, description="DEBE ser llenado si tipo_documento es 'CV'. Si no es CV, DEBE ser nulo (None).")
    datos_ci: Optional[DatosCI] = Field(None, description="DEBE ser llenado si tipo_documento es 'CI'. Si no es CI, DEBE ser nulo (None).")