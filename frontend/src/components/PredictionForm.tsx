
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { predictConsumo, getRecomendaciones } from '../api/energyapi'
import type { FormValues, PredictResponse } from '../types/energy'
import { ResultCard } from '../components/ResultCard'
import { RecoPanel } from '../components/RecoPanel'

// ── Mapeo de rango térmico ────────────────────────────────────────────────
const RANGO_LABELS: Record<string, string> = {
  '0': 'Bajo',
  '1': 'Medio',
  '2': 'Alto',
}

// ── Construye el JSON para POST /predict ─────────────────────────────────
function buildPredictPayload(form: FormValues) {
  return {
    temperatura_sala:          Number(form.temperatura_sala),
    consumo_iluminacion:       Number(form.consumo_iluminacion),
    temperatura_exterior:      Number(form.temperatura_exterior),
    humedad_exterior:          Number(form.humedad_exterior),
    temperatura_meteorologica: Number(form.temperatura_meteorologica),
    hora:                      Number(form.hora),
    dia_semana:                Number(form.dia_semana),
    mes:                       Number(form.mes),
    es_fin_de_semana_enc:      parseInt(form.fin_de_semana),
    rango_termico_enc:         parseInt(form.rango_termico),
  }
}

// ── Construye el JSON para POST /recommendations ──────────────────────────
function buildRecoPayload(form: FormValues, consumoPredicho: number) {
  return {
    consumo_predicho:          consumoPredicho,
    temperatura_sala:          Number(form.temperatura_sala),
    consumo_iluminacion:       Number(form.consumo_iluminacion),
    temperatura_exterior:      Number(form.temperatura_exterior),
    humedad_exterior:          Number(form.humedad_exterior),
    temperatura_meteorologica: Number(form.temperatura_meteorologica),
    hora:                      Number(form.hora),
    dia_semana:                Number(form.dia_semana),
    mes:                       Number(form.mes),
    es_fin_de_semana:          parseInt(form.fin_de_semana),
    rango_termico:             RANGO_LABELS[form.rango_termico], // texto, no número
  }
}

// ── Componente auxiliar: un campo del formulario ──────────────────────────
function Field({
  label,
  children,
  error,
}: {
  label: string
  children: React.ReactNode
  error?: string
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs text-slate-400 font-mono uppercase tracking-wider">
        {label}
      </label>
      {children}
      {error && <span className="text-xs text-red-400">{error}</span>}
    </div>
  )
}

// ── Componente auxiliar: caja de error ────────────────────────────────────
function ErrorBox({ message }: { message: string }) {
  return (
    <div className="bg-red-950 border border-red-800 rounded-lg px-4 py-3 text-sm text-red-400 font-mono">
      ❌ {message}
    </div>
  )
}

// ── Estilos reutilizables para inputs y selects ───────────────────────────
const inputClass =
  'w-full bg-[#111c30] border border-[#1a2d4a] rounded-lg px-3 py-2 text-white text-sm font-mono outline-none focus:border-blue-600 transition-colors'

// ── Componente principal ──────────────────────────────────────────────────
export function PredictionForm() {
  const [resultado, setResultado]     = useState<PredictResponse | null>(null)
  const [recos, setRecos]             = useState<string | null>(null)
  const [error, setError]             = useState<string | null>(null)
  const [loading, setLoading]         = useState(false)
  const [loadingReco, setLoadingReco] = useState(false)

  const {
    register,
    handleSubmit,
    getValues,
    formState: { errors },
  } = useForm<FormValues>({
    defaultValues: {
      temperatura_sala:          20.5,
      consumo_iluminacion:       30,
      temperatura_exterior:      7,
      humedad_exterior:          92,
      temperatura_meteorologica: 6.6,
      hora:                      17,
      dia_semana:                0,
      mes:                       1,
      fin_de_semana:             '0',
      rango_termico:             '1',
    },
  })

  // ── Submit: llama a /predict ────────────────────────────────────────────
  const onSubmit = async (form: FormValues) => {
    setLoading(true)
    setError(null)
    setRecos(null)
    try {
      const payload = buildPredictPayload(form)
      const data    = await predictConsumo(payload)
      setResultado(data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  // ── Botón de recomendaciones: llama a /recommendations ─────────────────
  const handleRecos = async () => {
    if (!resultado) return
    setLoadingReco(true)
    setError(null)
    try {
      const form    = getValues()
      const payload = buildRecoPayload(form, resultado.consumo_electrodomesticos)
      const data    = await getRecomendaciones(payload)
      setRecos(data.recomendaciones)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al obtener recomendaciones')
    } finally {
      setLoadingReco(false)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

      {/* ── Panel izquierdo: formulario ─────────────────────────────────── */}
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="bg-[#0d1525] border border-[#1a2d4a] rounded-xl p-6 flex flex-col gap-4"
      >
        <h2 className="text-blue-400 font-bold text-lg">Parámetros de entrada</h2>
        <p className="text-xs text-slate-500 font-mono -mt-2">
          Ingresa los datos
        </p>

        <div className="grid grid-cols-2 gap-4">

          <Field label="Temp. sala (°C)" error={errors.temperatura_sala?.message}>
            <input
              type="number" step="0.1" className={inputClass}
              {...register('temperatura_sala', { required: 'Requerido', valueAsNumber: true })}
            />
          </Field>

          <Field label="Temp. exterior (°C)" error={errors.temperatura_exterior?.message}>
            <input
              type="number" step="0.1" className={inputClass}
              {...register('temperatura_exterior', { required: 'Requerido', valueAsNumber: true })}
            />
          </Field>

          <Field label="Temp. meteorológica (°C)" error={errors.temperatura_meteorologica?.message}>
            <input
              type="number" step="0.1" className={inputClass}
              {...register('temperatura_meteorologica', { required: 'Requerido', valueAsNumber: true })}
            />
          </Field>

          <Field label="Humedad exterior (%)" error={errors.humedad_exterior?.message}>
            <input
              type="number" step="0.1" className={inputClass}
              {...register('humedad_exterior', { required: 'Requerido', valueAsNumber: true })}
            />
          </Field>

          <Field label="Consumo iluminación (Wh)" error={errors.consumo_iluminacion?.message}>
            <input
              type="number" step="0.1" className={inputClass}
              {...register('consumo_iluminacion', { required: 'Requerido', valueAsNumber: true })}
            />
          </Field>

          <Field label="Hora del día (0–23)" error={errors.hora?.message}>
            <input
              type="number" min={0} max={23} className={inputClass}
              {...register('hora', { required: 'Requerido', valueAsNumber: true, min: 0, max: 23 })}
            />
          </Field>

          <Field label="Día de la semana">
            <select className={inputClass} {...register('dia_semana', { valueAsNumber: true })}>
              <option value={0}>Lunes</option>
              <option value={1}>Martes</option>
              <option value={2}>Miércoles</option>
              <option value={3}>Jueves</option>
              <option value={4}>Viernes</option>
              <option value={5}>Sábado</option>
              <option value={6}>Domingo</option>
            </select>
          </Field>

          <Field label="Mes">
            <select className={inputClass} {...register('mes', { valueAsNumber: true })}>
              {['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
                .map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
            </select>
          </Field>

        
          <Field label="¿Fin de semana?">
            <select className={inputClass} {...register('fin_de_semana')}>
              <option value="0">Sí</option>
              <option value="1">No</option>
            </select>
          </Field>

        
          <Field label="Rango térmico">
            <select className={inputClass} {...register('rango_termico')}>
              <option value="0">Bajo</option>
              <option value="1">Medio</option>
              <option value="2">Alto</option>
            </select>
          </Field>

        </div>

        <button
          type="submit"
          disabled={loading}
          className="mt-2 w-full bg-blue-700 hover:bg-blue-600 disabled:opacity-50
            text-white font-bold py-3 rounded-lg transition-colors text-sm tracking-wide"
        >
          {loading ? 'Prediciendo...' : '⚡ Predecir consumo'}
        </button>
      </form>

      {/* ── Panel derecho: resultados ───────────────────────────────────── */}
      <div className="flex flex-col gap-4">
        {error && <ErrorBox message={error} />}

        {resultado && (
          <ResultCard
            data={resultado}
            onRecos={handleRecos}
            loadingReco={loadingReco}
          />
        )}

        {recos && <RecoPanel texto={recos} />}

        {!resultado && !error && (
          <div className="flex-1 bg-[#0d1525] border border-[#1a2d4a] border-dashed
            rounded-xl p-8 flex flex-col items-center justify-center text-center gap-3">
            <span className="text-3xl">⚡</span>
            <p className="text-slate-400 text-sm">
              Completa los parámetros y presiona<br />
              <span className="text-blue-400 font-mono">Predecir consumo</span>
            </p>
          </div>
        )}
      </div>

    </div>
  )
}