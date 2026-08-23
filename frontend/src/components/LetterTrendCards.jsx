import './LetterTrendCards.css'

function LetterTrendCards({ driftStatus }) {
  if (!driftStatus || !driftStatus.drift_status) {
    return null
  }

  const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

  const getTrendInfo = (letterStatus) => {
    const pRecent = letterStatus.p_hat_recent
    const lowerBound = letterStatus.lower_bound
    const upperBound = letterStatus.upper_bound
    const zScore = letterStatus.z_score || 0

    // Determine trend based on position relative to CI
    let trend = 'flat'
    let arrow = '─'
    let trendClass = 'flat'

    if (pRecent > upperBound) {
      trend = 'up'
      arrow = '▲'
      trendClass = 'up'
    } else if (pRecent < lowerBound) {
      trend = 'down'
      arrow = '▼'
      trendClass = 'down'
    }

    return { trend, arrow, trendClass, zScore }
  }

  return (
    <div className="letter-trend-cards">
      <h3 className="trend-cards-title">Per-Letter Trends</h3>
      <div className="trend-cards-grid">
        {letters.map(letter => {
          const letterStatus = driftStatus.drift_status[letter]
          if (!letterStatus) return null

          const { arrow, trendClass, zScore } = getTrendInfo(letterStatus)
          const pRecent = (letterStatus.p_hat_recent * 100).toFixed(1)
          const lowerBound = (letterStatus.lower_bound * 100).toFixed(1)
          const upperBound = (letterStatus.upper_bound * 100).toFixed(1)
          const consecutiveViolations = letterStatus.consecutive_violations || 0

          return (
            <div key={letter} className={`trend-card ${trendClass}`}>
              <div className="trend-card-header">
                <span className="trend-letter">{letter}</span>
                <span className="trend-arrow">{arrow}</span>
              </div>
              <div className="trend-card-body">
                <div className="trend-recent">
                  Recent: <strong>{pRecent}%</strong>
                </div>
                <div className="trend-baseline">
                  Baseline: {lowerBound}%–{upperBound}%
                </div>
                {consecutiveViolations > 0 && (
                  <div className="trend-violations">
                    {consecutiveViolations} consecutive {consecutiveViolations === 1 ? 'violation' : 'violations'}
                  </div>
                )}
                {Math.abs(zScore) > 0 && (
                  <div className="trend-zscore" title="Z-score from two-proportion test">
                    z = {zScore.toFixed(2)}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default LetterTrendCards
