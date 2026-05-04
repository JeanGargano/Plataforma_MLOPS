from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    """
    Datos de entrada para la predicción de consumo energético.
    Corresponde exactamente a las features del modelo entrenado.
    """
    temperatura_sala          : float = Field(..., example=20.5,  description="Temperatura interior de la sala en °C")
    consumo_iluminacion       : float = Field(..., example=30.0,  description="Consumo de iluminación en Wh")
    temperatura_exterior      : float = Field(..., example=7.0,   description="Temperatura exterior en °C")
    humedad_exterior          : float = Field(..., example=92.0,  description="Humedad exterior en %")
    temperatura_meteorologica : float = Field(..., example=6.6,   description="Temperatura meteorológica en °C")
    hora                      : int   = Field(..., example=17,    description="Hora del día (0-23)", ge=0, le=23)
    dia_semana                : int   = Field(..., example=0,     description="Día de la semana (0=lunes, 6=domingo)", ge=0, le=6)
    mes                       : int   = Field(..., example=1,     description="Mes del año (1-12)", ge=1, le=12)
    es_fin_de_semana          : int   = Field(..., example=0,     description="1 si es fin de semana, 0 si no", ge=0, le=1)
    rango_termico             : str   = Field(..., example="Medio", description="Rango térmico: Bajo / Medio / Alto")


class PredictionOutput(BaseModel):
    """Respuesta de la predicción."""
    consumo_electrodomesticos : float
    modelo_version            : str
    unidad                    : str = "Wh"


class HealthResponse(BaseModel):
    status        : str
    model_loaded  : bool
    modelo_version: str