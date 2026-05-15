// ── Lo que ENVIAMOS al backend (POST /predict) ──────────────────────
export interface PredictRequest {
  temperatura_sala:          number;
  consumo_iluminacion:       number;
  temperatura_exterior:      number;
  humedad_exterior:          number;
  temperatura_meteorologica: number;
  hora:                      number;  
  dia_semana:                number; 
  mes:                       number;   
  es_fin_de_semana_enc:      number;   
  rango_termico_enc:         number;   
}
 
// ── Lo que RECIBIMOS del backend (respuesta de /predict) ─────────────
export interface PredictResponse {
  consumo_electrodomesticos: number;   
  modelo_version:            string;   
  unidad:                    string;   
}
 
// ── Lo que ENVIAMOS al backend (POST /recommendations) ───────────────
export interface RecoRequest {
  consumo_predicho:          number;
  temperatura_sala:          number;
  consumo_iluminacion:       number;
  temperatura_exterior:      number;
  humedad_exterior:          number;
  temperatura_meteorologica: number;
  hora:                      number;
  dia_semana:                number;
  mes:                       number;
  es_fin_de_semana:          number;   
  rango_termico:             string;   
}
 
// ── Lo que RECIBIMOS de /recommendations ─────────────────────────────
export interface RecoResponse {
  recomendaciones: string;   
  consumo_predicho: number;
  nivel_consumo:    string;
}
 
// ── Tipo auxiliar para el formulario (valores que ve el usuario) ──────
export interface FormValues {
  temperatura_sala:          number;
  consumo_iluminacion:       number;
  temperatura_exterior:      number;
  humedad_exterior:          number;
  temperatura_meteorologica: number;
  hora:                      number;
  dia_semana:                number;
  mes:                       number;
  // Estos dos se convierten antes de enviar al backend
  fin_de_semana: '0' | '1';  
  rango_termico: '0' | '1' | '2'; 
}
