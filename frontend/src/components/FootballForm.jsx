import { useState } from 'react'
import { predictFootball } from '../api'
import PredictionResult from './PredictionResult'
import ErrorMessage from './ErrorMessage'

const PL_TEAMS = [
  'AFC Bournemouth', 'Arsenal FC', 'Aston Villa FC', 'Brentford FC',
  'Brighton & Hove Albion FC', 'Burnley FC', 'Chelsea FC', 'Crystal Palace FC',
  'Everton FC', 'Fulham FC', 'Liverpool FC', 'Luton Town FC',
  'Manchester City FC', 'Manchester United FC', 'Newcastle United FC',
  'Nottingham Forest FC', 'Sheffield United FC', 'Tottenham Hotspur FC',
  'West Ham United FC', 'Wolverhampton Wanderers FC',
]

const inputCls = 'w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors'
const labelCls = 'block text-sm font-medium text-slate-300 mb-1'

export default function FootballForm() {
  const [form, setForm] = useState({ home_team: '', away_team: '', matchday: '' })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const set = (key) => (e) => {
    setForm((f) => ({ ...f, [key]: e.target.value }))
    setResult(null)
    setError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.home_team || !form.away_team) return setError('Please select both teams.')
    if (form.home_team === form.away_team) return setError('Teams must be different.')

    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await predictFootball({
        home_team: form.home_team,
        away_team: form.away_team,
        matchday: Number(form.matchday),
      })
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.error || 'Prediction failed. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className={labelCls}>Home Team</label>
          <select className={inputCls} value={form.home_team} onChange={set('home_team')} required>
            <option value="">Select team...</option>
            {PL_TEAMS.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
        <div>
          <label className={labelCls}>Away Team</label>
          <select className={inputCls} value={form.away_team} onChange={set('away_team')} required>
            <option value="">Select team...</option>
            {PL_TEAMS.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
      </div>

      <div className="sm:w-1/3">
        <label className={labelCls}>Matchday</label>
        <input
          type="number" min="1" max="38" required
          className={inputCls} placeholder="1–38"
          value={form.matchday} onChange={set('matchday')}
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors duration-200 flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            Predicting…
          </>
        ) : '⚽ Predict Result'}
      </button>

      <ErrorMessage message={error} onDismiss={() => setError(null)} />
      <PredictionResult sport="football" result={result} />
    </form>
  )
}
