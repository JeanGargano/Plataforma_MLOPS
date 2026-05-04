from pydantic import BaseModel, Field


class RecommendationInput(BaseModel):
    """
    Datos de entrada para generar recomendaciones.
    Combina el contexto del usuario con el resultado de la predicción.
    """
    # Resultado de la predicción
    consumo_predicho          : float = Field(..., example=97.5,
                                              description="Consumo predicho en Wh")

    # Contexto del entorno (mismo input que /predict)
    temperatura_sala          : float = Field(..., example=20.5)
    consumo_iluminacion       : float = Field(..., example=30.0)
    temperatura_exterior      : float = Field(..., example=7.0)
    humedad_exterior          : float = Field(..., example=92.0)
    temperatura_meteorologica : float = Field(..., example=6.6)
    hora                      : int   = Field(..., example=17)
    dia_semana                : int   = Field(..., example=0)
    mes                       : int   = Field(..., example=1)
    es_fin_de_semana          : int   = Field(..., example=0)
    rango_termico             : str   = Field(..., example="Medio")


class RecommendationOutput(BaseModel):
    """Respuesta con las recomendaciones generadas por Gemini."""
    recomendaciones : str
    consumo_predicho: float
    nivel_consumo   : str   # Bajo / Medio / Alto