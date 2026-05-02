import { useState } from 'react'
import CricketForm from './components/CricketForm'
import FootballForm from './components/FootballForm'

const tabs = [
  { id: 'cricket',  label: '🏏 Cricket',  desc: 'ODI Match Predictor' },
  { id: 'football', label: '⚽ Football', desc: 'Premier League Predictor' },
]

export default function App() {
  const [active, setActive] = useState('cricket')
  const current = tabs.find((t) => t.id === active)

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 shadow-xl">
        <div className="max-w-3xl mx-auto px-4 py-5">
          <div className="flex items-center gap-3 mb-5">
            <span className="text-3xl">🏆</span>
            <div>
              <h1 className="text-xl font-bold text-white leading-tight">Sports Predictor</h1>
              <p className="text-slate-400 text-xs">ML-powered match predictions</p>
            </div>
          </div>

          {/* Tab bar */}
          <div className="flex gap-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActive(tab.id)}
                className={`flex-1 sm:flex-none px-5 py-2.5 rounded-xl font-semibold text-sm transition-all duration-200 ${
                  active === tab.id
                    ? tab.id === 'cricket'
                      ? 'bg-green-600 text-white shadow-lg shadow-green-900/40'
                      : 'bg-blue-600 text-white shadow-lg shadow-blue-900/40'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 shadow-xl">
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-white">{current.label}</h2>
            <p className="text-slate-400 text-sm">{current.desc}</p>
          </div>

          {active === 'cricket' ? <CricketForm /> : <FootballForm />}
        </div>

        <p className="text-center text-slate-600 text-xs mt-6">
          Powered by RandomForest · Cricket 72% accuracy · Football 45% accuracy
        </p>
      </main>
    </div>
  )
}
