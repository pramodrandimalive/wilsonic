import './HistoryTable.css'

function HistoryTable({ draws }) {
  if (!draws || draws.length === 0) {
    return (
      <div className="history-card">
        <h2>Recent Draws</h2>
        <p className="no-data">No draws yet</p>
      </div>
    )
  }

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} min${diffMins === 1 ? '' : 's'} ago`
    if (diffMins < 1440) {
      const hours = Math.floor(diffMins / 60)
      return `${hours} hour${hours === 1 ? '' : 's'} ago`
    }
    
    // Format as date/time
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="history-card">
      <h2>Recent Draws</h2>
      <p className="section-description">
        Last 10 draws, most recent first
      </p>

      <div className="history-table">
        <div className="table-header">
          <div className="col-letter">Letter</div>
          <div className="col-time">Time</div>
          <div className="col-source">Source</div>
        </div>
        
        {draws.map((draw, index) => (
          <div 
            key={draw.id} 
            className={`table-row ${index === 0 ? 'latest' : ''}`}
          >
            <div className="col-letter">
              <span className="letter-badge">{draw.letter}</span>
            </div>
            <div className="col-time">
              {formatTimestamp(draw.timestamp)}
            </div>
            <div className="col-source">
              <span className={`source-badge ${draw.source}`}>
                {draw.source}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default HistoryTable
