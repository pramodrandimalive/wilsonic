import './DriftIndicator.css'

function DriftIndicator({ driftStatus }) {
  if (!driftStatus) {
    return null
  }

  const { any_drift_detected, drifted_letters, letters_at_risk, insufficient_data, message } = driftStatus

  // Insufficient data - show info message
  if (insufficient_data) {
    return (
      <div className="drift-indicator info">
        <div className="drift-icon">ⓘ</div>
        <div className="drift-content">
          <strong>Drift Detection Inactive</strong>
          <p>{message || 'Not enough data yet for drift detection'}</p>
        </div>
      </div>
    )
  }

  if (!any_drift_detected && letters_at_risk.length === 0) {
    return (
      <div className="drift-indicator success">
        <div className="drift-icon">✓</div>
        <div className="drift-content">
          <strong>All Clear</strong>
          <p>Recent patterns match historical baseline</p>
        </div>
      </div>
    )
  }

  if (any_drift_detected) {
    return (
      <div className="drift-indicator warning">
        <div className="drift-icon">⚠</div>
        <div className="drift-content">
          <strong>Drift Detected</strong>
          <p>
            {drifted_letters.length === 1 
              ? `Letter ${drifted_letters[0]} has` 
              : `Letters ${drifted_letters.join(', ')} have`} 
            {' '}drifted from historical patterns (10+ consecutive violations)
          </p>
          {letters_at_risk.length > 0 && (
            <p className="at-risk">
              At risk: {letters_at_risk.join(', ')} (5+ violations)
            </p>
          )}
        </div>
      </div>
    )
  }

  if (letters_at_risk.length > 0) {
    return (
      <div className="drift-indicator info">
        <div className="drift-icon">ⓘ</div>
        <div className="drift-content">
          <strong>Monitoring</strong>
          <p>
            {letters_at_risk.length === 1 
              ? `Letter ${letters_at_risk[0]} is` 
              : `Letters ${letters_at_risk.join(', ')} are`} 
            {' '}showing variation (5+ consecutive violations, not yet flagged)
          </p>
        </div>
      </div>
    )
  }

  return null
}

export default DriftIndicator
