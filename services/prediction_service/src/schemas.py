from pydantic import BaseModel, Field
from pydantic import ConfigDict


class PredictionInput(BaseModel):
    temperatura_sala          : float = Field(..., example=20.5)
    consumo_iluminacion       : float = Field(..., example=30.0)
    temperatura_exterior      : float = Field(..., example=7.0)
    humedad_exterior          : float = Field(..., example=92.0)
    temperatura_meteorologica : float = Field(..., example=6.6)
    hora                      : int   = Field(..., example=17,  ge=0, le=23)
    dia_semana                : int   = Field(..., example=0,   ge=0, le=6)
    mes                       : int   = Field(..., example=1,   ge=1, le=12)
    es_fin_de_semana_enc          : int   = Field(..., example=0,   ge=0, le=1)
    rango_termico_enc             : int   = Field(..., example=1,   ge=0,
                                             description="0=Bajo, 1=Medio, 2=Alto")


class PredictionOutput(BaseModel):
    consumo_electrodomesticos : float
    modelo_version            : str
    unidad                    : str = "Wh"


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status        : str
    model_loaded  : bool
    modelo_version: str