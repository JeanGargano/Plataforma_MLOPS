import os
from fastapi import FastAPI, HTTPException
from schemas import RecommendationInput, RecommendationOutput
from groq_client import get_recommendations
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Recommendation Service — Energy Efficiency",
    description="Genera recomendaciones de eficiencia energética usando Groq API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    groq_key_set = bool(os.getenv("GROQ_API_KEY", ""))
    return {
        "status"         : "ok",
        "service"        : "recommendation-service",
        "groq_key_set" : groq_key_set
    }


@app.post("/recommendations", response_model=RecommendationOutput)
def recommendations(data: RecommendationInput):
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY no configurada en el servidor"
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
            detail=f"Error al consultar Groq API: {str(e)}"
        )