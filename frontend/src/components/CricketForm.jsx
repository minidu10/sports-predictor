import { useState } from 'react'
import { predictCricket } from '../api'
import PredictionResult from './PredictionResult'
import ErrorMessage from './ErrorMessage'

const CRICKET_TEAMS = [
  'Africa XI', 'Asia XI', 'Australia', 'Bangladesh', 'Bermuda', 'Canada',
  'England', 'Hong Kong', 'ICC World XI', 'India', 'Ireland', 'Jersey',
  'Kenya', 'Namibia', 'Nepal', 'Netherlands', 'New Zealand', 'Oman',
  'Pakistan', 'Papua New Guinea', 'Scotland', 'South Africa', 'Sri Lanka',
  'Thailand', 'United Arab Emirates', 'United States of America',
  'West Indies', 'Zimbabwe',
]

const inputCls = 'w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 transition-colors'
const labelCls = 'block text-sm font-medium text-slate-300 mb-1'

export default function CricketForm() {
  const [form, setForm] = useState({
    team1: '', team2: '',
    inn1_runs: '', inn1_wickets: '', inn1_balls: '',
  })
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
    if (!form.team1 || !form.team2) return setError('Please select both teams.')
    if (form.team1 === form.team2) return setError('Teams must be different.')

    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await predictCricket({
        team1: form.team1,
        team2: form.team2,
        inn1_runs: Number(form.inn1_runs),
        inn1_wickets: Number(form.inn1_wickets),
        inn1_balls: Number(form.inn1_balls),
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
          <label className={labelCls}>Batting Team (Innings 1)</label>
          <select className={inputCls} value={form.team1} onChange={set('team1')} required>
            <option value="">Select team...</option>
            {CRICKET_TEAMS.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
        <div>
          <label className={labelCls}>Chasing Team (Innings 2)</label>
          <select className={inputCls} value={form.team2} onChange={set('team2')} required>
            <option value="">Select team...</option>
            {CRICKET_TEAMS.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label className={labelCls}>Innings 1 Runs</label>
          <input
            type="number" min="0" max="600" required
            className={inputCls} placeholder="e.g. 287"
            value={form.inn1_runs} onChange={set('inn1_runs')}
          />
        </div>
        <div>
          <label className={labelCls}>Innings 1 Wickets</label>
          <input
            type="number" min="0" max="10" required
            className={inputCls} placeholder="0–10"
            value={form.inn1_wickets} onChange={set('inn1_wickets')}
          />
        </div>
        <div>
          <label className={labelCls}>Innings 1 Balls</label>
          <input
            type="number" min="1" max="360" required
            className={inputCls} placeholder="e.g. 300"
            value={form.inn1_balls} onChange={set('inn1_balls')}
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-green-600 hover:bg-green-500 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors duration-200 flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            Predicting…
          </>
        ) : '🏏 Predict Winner'}
      </button>

      <ErrorMessage message={error} onDismiss={() => setError(null)} />
      <PredictionResult sport="cricket" result={result} />
    </form>
  )
}
