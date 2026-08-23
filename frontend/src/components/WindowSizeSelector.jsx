import './WindowSizeSelector.css'

function WindowSizeSelector({ value, onChange }) {
  const options = [100, 300, 500, 1000, 5000, 10000, 50000, 100000]
  
  const formatSize = (size) => {
    if (size >= 1000) {
      return `${size / 1000}k draws`
    }
    return `${size} draws`
  }
  
  return (
    <div className="window-selector">
      <label htmlFor="window-size">Analysis Window:</label>
      <select 
        id="window-size" 
        value={value} 
        onChange={(e) => onChange(Number(e.target.value))}
      >
        {options.map(size => (
          <option key={size} value={size}>
            {formatSize(size)}
          </option>
        ))}
      </select>
      <p className="window-note">
        Smaller windows react faster but show more natural statistical 
        fluctuation. Larger windows are more stable but slower to detect 
        real changes.
      </p>
    </div>
  )
}

export default WindowSizeSelector
