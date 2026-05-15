import type { PredictResponse } from '../types/energy'
 
interface Props {
  data:        PredictResponse
  onRecos:     () => void
  loadingReco: boolean
}
 
function getNivel(wh: number) {
  if (wh < 80)  return { label: 'Bajo',  color: 'text-green-400',  pct: 25 }
  if (wh < 150) return { label: 'Medio', color: 'text-yellow-400', pct: 60 }
  return              { label: 'Alto',  color: 'text-red-400',    pct: 90 }
}
 
export function ResultCard({ data, onRecos, loadingReco }: Props) {
  const nivel = getNivel(data.consumo_electrodomesticos)
 
  return (
    <div className="bg-[#0d1525] border border-[#1f3660] rounded-xl p-6">
      <p className="text-xs text-slate-500 font-mono uppercase tracking-wider mb-2">
        Consumo estimado
      </p>
      <div className="flex items-end gap-2">
        <span className="text-4xl font-bold text-blue-400 font-mono">
          {data.consumo_electrodomesticos.toFixed(1)}
        </span>
        <span className="text-slate-400 mb-1">Wh</span>
      </div>
      <p className={`text-sm font-semibold mt-1 ${nivel.color}`}>
        Nivel de consumo: {nivel.label}
      </p>
      <p className="text-xs text-slate-600 font-mono mt-1">{data.modelo_version}</p>
 
      {/* Barra de nivel */}
      <div className="h-1 bg-slate-800 rounded mt-4 overflow-hidden">
        <div
          className="h-full bg-blue-500 rounded transition-all duration-700"
          style={{ width: `${nivel.pct}%` }}
        />
      </div>
 
      <button onClick={onRecos} disabled={loadingReco}
        className="mt-4 w-full border border-[#1f3660] text-blue-400 hover:bg-[#1a2d4a] py-2 rounded-lg text-sm font-semibold">
        {loadingReco ? 'Consultando IA...' : 'Generar recomendaciones con IA'}
      </button>
    </div>
  )
}
