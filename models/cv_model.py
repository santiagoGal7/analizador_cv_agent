from pydantic import BaseModel, Field
from typing import List

class AnalisisCV(BaseModel):
    nombre_candidato: str = Field(description="Nombre completo del candidato encontrado en la Hoja de Vida.")
    experiencia_anos: int = Field(description="Cantidad total de años de experiencia laboral del candidato.")
    habilidades_clave: List[str] = Field(description="Lista de las principales habilidades técnicas y blandas del perfil.")
    education: str = Field(description="Nivel educativo, títulos obtenidos e instituciones académicas.")
    experiencia_relevante: str = Field(description="Resumen conciso de los cargos anteriores más afines a la vacante.")
    fotalezas: List[str] = Field(description="Puntos fuertes del candidato en relación con el puesto solicitado.")
    areas_mejora: List[str] = Field(description="Vacíos técnicos o habilidades que el candidato necesita reforzar.")
    porcentaje_ajuste: int = Field(description="Porcentaje de compatibilidad total con la vacante (de 0 a 100).", ge=0, le=100)