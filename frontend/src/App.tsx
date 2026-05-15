import { PredictionForm } from './components/PredictionForm'

export default function App() {
  // Funciones para abrir servicios
  const openMonitoring = () => {
    window.open('http://localhost:3001', '_blank')
  }

  const openTraining = () => {
    window.open('http://localhost:5000', '_blank')
  }

  const openPrediction = () => {
    window.location.reload()
  }

  return (
    <div className="flex min-h-screen bg-[#080c14] text-white">

      {/* ── Barra lateral ─────────────────────────────────── */}
      <aside className="w-64 bg-[#0d1525] border-r border-[#1a2d4a] p-6 flex flex-col">

        {/* Logo */}
        <div className="flex items-center gap-3 pb-6 border-b border-[#1a2d4a] mb-4">
          <div className="w-9 h-9 bg-blue-700 rounded-lg flex items-center justify-center">
            <span className="text-white text-lg">⚡</span>
          </div>

          <div>
            <p className="font-bold text-sm">MLOps Energy</p>
            <p className="text-xs text-slate-500 font-mono">
              v1.0 · Production
            </p>
          </div>
        </div>

        {/* Navegacion */}
        <nav className="flex flex-col gap-1">

          <NavItem
            icon="⚡"
            label="Prediccion"
            active
            onClick={openPrediction}
          />

          <NavItem
            icon="📊"
            label="Monitoreo"
            onClick={openMonitoring}
          />

          <NavItem
            icon="🧠"
            label="Entrenamiento"
            onClick={openTraining}
          />

        </nav>

        {/* Links a servicios externos */}
        <div className="mt-4 pt-4 border-t border-[#1a2d4a] flex flex-col gap-1">

          <p className="text-xs text-slate-600 font-mono uppercase tracking-wider px-3 mb-1">
            Servicios
          </p>

          <ExternalLink
            href="http://localhost:5000"
            label="MLflow UI"
          />

          <ExternalLink
            href="http://localhost:3001"
            label="Grafana"
          />

          <ExternalLink
            href="http://localhost:9090"
            label="Prometheus"
          />

          <ExternalLink
            href="http://localhost:8001/docs"
            label="Swagger API"
          />

          <ExternalLink
            href="http://localhost:8004/metrics"
            label="Metrics API"
          />

        </div>

        {/* Info del modelo activo */}
        <div className="mt-auto bg-[#111c30] border border-[#1a2d4a] rounded-xl p-3">

          <p className="text-sm text-blue-400 font-mono mt-1">
            Grupo de Desarrollo
          </p>

          <p className="text-xs text-slate-600 font-mono">
            Jean Alfred Gargano
            Karen Gisel López
            Juan Felipe Plata Barbosa
            Juan Manuel Lame 
            Mónica Chicangana
          </p>

        </div>
      </aside>

      {/* ── Contenido principal ──────────────────────────── */}
      <main className="flex-1 flex flex-col">

        {/* Topbar */}
        <header
          className="bg-[#0d1525] border-b border-[#1a2d4a] px-8 py-4
          flex items-center justify-between"
        >

          <div>
            <h1 className="text-lg font-bold">
              Prediccion de consumo
            </h1>

            <p className="text-xs text-slate-500 font-mono">
              Ingresa el contexto ambiental y temporal
            </p>
          </div>

          <span
            className="text-xs font-mono text-blue-400 bg-blue-950
            border border-blue-800 px-3 py-1 rounded-full"
          >
            ● Computación en la nube
          </span>

        </header>

        {/* Formulario y resultados */}
        <div className="flex-1 p-8 overflow-y-auto">
          <PredictionForm />
        </div>

      </main>
    </div>
  )
}


// ── COMPONENTES AUXILIARES ─────────────────────────────────────

function NavItem({
  icon,
  label,
  active,
  onClick,
}: {
  icon: string
  label: string
  active?: boolean
  onClick?: () => void
}) {

  return (
    <button
      onClick={onClick}
      className={`
        flex items-center gap-3 px-3 py-2 rounded-lg text-sm
        w-full text-left transition-all duration-200

        ${
          active
            ? 'bg-blue-950 text-blue-400 border border-blue-900'
            : 'text-slate-400 hover:bg-[#111c30] hover:text-white'
        }
      `}
    >
      <span>{icon}</span>
      {label}
    </button>
  )
}


function ExternalLink({
  href,
  label,
}: {
  href: string
  label: string
}) {

  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="
        flex items-center gap-2 px-3 py-2 rounded-lg text-xs
        text-slate-500 hover:text-slate-300 hover:bg-[#111c30]
        font-mono transition-all duration-200
      "
    >
      {label} ↗
    </a>
  )
}