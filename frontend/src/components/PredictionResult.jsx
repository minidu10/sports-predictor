function Bar({ label, value, isTop }) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between text-sm font-medium">
        <span className={isTop ? 'text-green-400' : 'text-slate-300'}>{label}</span>
        <span className={isTop ? 'text-green-400 font-bold' : 'text-slate-400'}>{value}%</span>
      </div>
      <div className="h-3 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${isTop ? 'bg-green-500' : 'bg-slate-500'}`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  )
}

export default function PredictionResult({ sport, result }) {
  if (!result) return null

  if (sport === 'cricket') {
    const winnerProb = result.win_probability
    const loserProb = Math.round((100 - winnerProb) * 10) / 10
    const loser = result.winner === result.team1 ? result.team2 : result.team1

    return (
      <div className="mt-6 bg-slate-800 border border-slate-700 rounded-2xl p-6 animate-fade-in">
        <div className="text-center mb-5">
          <p className="text-slate-400 text-sm uppercase tracking-widest mb-1">Predicted Winner</p>
          <p className="text-2xl font-bold text-green-400">🏏 {result.winner}</p>
        </div>
        <div className="flex flex-col gap-3">
          <Bar label={result.winner} value={winnerProb} isTop={true} />
          <Bar label={loser} value={loserProb} isTop={false} />
        </div>
      </div>
    )
  }

  if (sport === 'football') {
    const probs = [
      { label: `🏠 ${result.home_team} (Home Win)`, value: result.home_win_prob },
      { label: '🤝 Draw', value: result.draw_prob },
      { label: `✈️ ${result.away_team} (Away Win)`, value: result.away_win_prob },
    ]
    const top = Math.max(result.home_win_prob, result.draw_prob, result.away_win_prob)

    return (
      <div className="mt-6 bg-slate-800 border border-slate-700 rounded-2xl p-6 animate-fade-in">
        <div className="text-center mb-5">
          <p className="text-slate-400 text-sm uppercase tracking-widest mb-1">Predicted Result</p>
          <p className="text-2xl font-bold text-green-400">⚽ {result.result}</p>
        </div>
        <div className="flex flex-col gap-3">
          {probs.map(({ label, value }) => (
            <Bar key={label} label={label} value={value} isTop={value === top} />
          ))}
        </div>
      </div>
    )
  }

  return null
}
