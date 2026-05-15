interface Props { texto: string }
 
export function RecoPanel({ texto }: Props) {
  // El backend devuelve: '1. Texto\n2. Texto\n3. Texto'
  const items = texto
    .split('\n')
    .filter(line => line.trim().match(/^\d+\./))  
    .map(line => line.replace(/^\d+\.\s*/, ''))   
 
  return (
    <div className="bg-[#0d1525] border border-[#1f3660] rounded-xl p-6">
      <h3 className="text-blue-400 font-bold mb-4">Recomendaciones IA</h3>
      <div className="flex flex-col divide-y divide-[#1a2d4a]">
        {items.map((item, i) => (
          <div key={i} className="flex gap-3 py-3">
            <span className="w-6 h-6 rounded-full bg-[#1a2d4a] border border-[#1f3660]
              text-blue-400 text-xs font-mono flex items-center justify-center flex-shrink-0">
              {i + 1}
            </span>
            <p className="text-slate-400 text-sm leading-relaxed">{item}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
