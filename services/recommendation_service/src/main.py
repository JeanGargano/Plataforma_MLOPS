import os
from fastapi import FastAPI, HTTPException
from schemas import RecommendationInput, RecommendationOutput
from gemini_client import get_recommendations


app = FastAPI(
    title="Recommendation Service — Energy Efficiency",
    description="Genera recomendaciones de eficiencia energética usando Gemini API",
    version="1.0.0"
)


@app.get("/health")
def health():
    gemini_key_set = bool(os.getenv("GEMINI_API_KEY", ""))
    return {
        "status"         : "ok",
        "service"        : "recommendation-service",
        "gemini_key_set" : gemini_key_set
    }


@app.post("/recommendations", response_model=RecommendationOutput)
def recommendations(data: RecommendationInput):
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY no configurada en el servidor"
        )

    try:
        input_dict = data.model_dump()
        recomendaciones, nivel_consumo = get_recommendations(input_dict)

        return RecommendationOutput(
            recomendaciones =recomendaciones,
            consumo_predicho=data.consumo_predicho,
            nivel_consumo   =nivel_consumo
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar Gemini API: {str(e)}"
        )