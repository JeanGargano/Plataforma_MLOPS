import os

from openai import OpenAI


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY no configurada")


client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.3-70b-versatile"


def clasificar_consumo(consumo_wh: float) -> str:

    if consumo_wh < 60:
        return "Bajo"

    elif consumo_wh < 200:
        return "Medio"

    return "Alto"


def construir_prompt(data: dict, nivel_consumo: str) -> str:

    return f"""
Eres un experto en eficiencia energética residencial.

CONTEXTO:
- Hora: {data['hora']}:00
- Temperatura sala: {data['temperatura_sala']}°C
- Temperatura exterior: {data['temperatura_exterior']}°C
- Humedad exterior: {data['humedad_exterior']}%
- Consumo iluminación: {data['consumo_iluminacion']} Wh

PREDICCIÓN:
- Consumo estimado: {data['consumo_predicho']} Wh
- Nivel: {nivel_consumo}

Genera exactamente 3 recomendaciones prácticas y personalizadas.

Formato:
1. [Título]: descripción
2. [Título]: descripción
3. [Título]: descripción

Responde en español.
"""


def get_recommendations(data: dict):

    nivel_consumo = clasificar_consumo(
        data["consumo_predicho"]
    )

    prompt = construir_prompt(
        data,
        nivel_consumo
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "Eres experto en eficiencia energética."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=500
    )

    recomendaciones = response.choices[0].message.content

    return recomendaciones, nivel_consumo