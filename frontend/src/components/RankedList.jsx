import './RankedList.css'

function RankedList({ ranking }) {
  if (!ranking || ranking.length === 0) {
    return (
      <div className="ranked-list-card">
        <h2>Letter Ranking</h2>
        <p className="no-data">No ranking data available</p>
      </div>
    )
  }

  return (
    <div className="ranked-list-card">
      <h2>Letter Ranking</h2>
      <p className="section-description">
        Letters sorted by probability (most to least likely)
      </p>
      
      <div className="ranked-list">
        {ranking.map((entry) => {
          const percentage = (entry.p_hat * 100).toFixed(1)
          const lowerBound = (entry.lower_bound * 100).toFixed(1)
          const upperBound = (entry.upper_bound * 100).toFixed(1)
          const barWidth = entry.p_hat * 100

          return (
            <div key={entry.letter} className="rank-item">
              <div className="rank-header">
                <div className="rank-number">#{entry.rank}</div>
                <div className="letter-large">{entry.letter}</div>
                <div className="percentage-large">{percentage}%</div>
              </div>
              
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ 
                    width: `${barWidth}%`,
                    backgroundColor: entry.rank === 1 ? '#2563eb' : '#64748b'
                  }}
                />
              </div>
              
              <div className="rank-details">
                <div className="detail-item">
                  <span className="detail-label">95% CI:</span>
                  <span className="detail-value">
                    {lowerBound}% – {upperBound}%
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Count:</span>
                  <span className="detail-value">
                    {entry.count.toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {ranking.length > 0 && (
        <div className="ranking-note">
          <strong>Most likely:</strong> {ranking[0].letter} ({(ranking[0].p_hat * 100).toFixed(1)}% probability)
        </div>
      )}
    </div>
  )
}

export default RankedList
