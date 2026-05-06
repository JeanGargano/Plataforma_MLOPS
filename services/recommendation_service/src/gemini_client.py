import os
from google import genai
from google.genai import types
 
 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = "gemini-2.0-flash-lite"
 
client = genai.Client(api_key=GEMINI_API_KEY)


def clasificar_consumo(consumo_wh: float) -> str:

    if consumo_wh < 60:
        return "Bajo"
    elif consumo_wh < 200:
        return "Medio"
    else:
        return "Alto"


def construir_prompt(data: dict, nivel_consumo: str) -> str:
    dia_map = {
        0: "lunes", 1: "martes", 2: "miércoles",
        3: "jueves", 4: "viernes", 5: "sábado", 6: "domingo"
    }

    mes_map = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }

    dia_texto = dia_map.get(data["dia_semana"], str(data["dia_semana"]))
    mes_texto = mes_map.get(data["mes"], str(data["mes"]))
    tipo_dia  = "fin de semana" if data["es_fin_de_semana"] else "día laboral"

    prompt = f"""
Eres un experto en eficiencia energética residencial. Analiza el siguiente contexto
de consumo energético y proporciona recomendaciones prácticas y específicas.

CONTEXTO DEL USUARIO:
- Fecha y hora      : {dia_texto} {tipo_dia}, {mes_texto}, hora {data['hora']}:00
- Temperatura sala  : {data['temperatura_sala']}°C
- Temperatura ext.  : {data['temperatura_exterior']}°C (meteorológica: {data['temperatura_meteorologica']}°C)
- Humedad exterior  : {data['humedad_exterior']}%
- Rango térmico     : {data['rango_termico']} (diferencia sala vs exterior)
- Consumo iluminación: {data['consumo_iluminacion']} Wh

RESULTADO DE LA PREDICCIÓN:
- Consumo estimado de electrodomésticos: {data['consumo_predicho']} Wh
- Nivel de consumo: {nivel_consumo}

TAREA:
Genera exactamente 3 recomendaciones prácticas y personalizadas para reducir
o optimizar el consumo energético, considerando el contexto específico del usuario.

Formato de respuesta:
1. [Título corto]: Descripción específica de la acción recomendada y su impacto esperado.
2. [Título corto]: Descripción específica de la acción recomendada y su impacto esperado.
3. [Título corto]: Descripción específica de la acción recomendada y su impacto esperado.

Sé concreto, usa los datos del contexto y evita recomendaciones genéricas.
Responde en español.
""".strip()

    return prompt


def get_recommendations(data: dict) -> tuple[str, str]:
    nivel_consumo = clasificar_consumo(data["consumo_predicho"])
    prompt        = construir_prompt(data, nivel_consumo)
 
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )
 
    return response.text, nivel_consumo
