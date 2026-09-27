import { useState, useEffect, useRef } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  ReferenceArea,
  Area
} from 'recharts'
import './RollingFrequencyChart.css'

// Binance-inspired color palette for chart lines
const LETTER_COLORS = {
  A: '#0ECB81',  // Success Green (Binance)
  B: '#FCD535',  // Primary Yellow (Binance)
  C: '#F6465D',  // Danger Red (Binance)
  D: '#3B82F6',  // Info Blue (Binance)
  E: '#B377F8',  // Accent Purple
  F: '#2DBDB6',  // Accent Cyan
  G: '#FFA726'   // Warning Orange
}

// White baselines for all letters
const BASELINE_COLORS = {
  A: '#FFFFFF',  // White
  B: '#FFFFFF',  // White
  C: '#FFFFFF',  // White
  D: '#FFFFFF',  // White
  E: '#FFFFFF',  // White
  F: '#FFFFFF',  // White
  G: '#FFFFFF'   // White
}

function RollingFrequencyChart({ trendData }) {
  const [visibleLetters, setVisibleLetters] = useState({
    A: true,
    B: true,
    C: true,
    D: true,
    E: true,
    F: true,
    G: true
  })
  
  const [showBaselines, setShowBaselines] = useState(false)
  const [showShading, setShowShading] = useState(true)
  const [isolatedLetter, setIsolatedLetter] = useState(null)
  
  // Zoom/Pan state
  const [xDomain, setXDomain] = useState(null) // [min, max] or null for full range
  const [isPanning, setIsPanning] = useState(false)
  const [panStart, setPanStart] = useState(null)
  const containerRef = useRef(null)

  if (!trendData || !trendData.data_points || trendData.data_points.length === 0) {
    return (
      <div className="trend-chart-container">
        <div className="trend-chart-empty">
          {trendData?.message || "Not enough data for trend analysis"}
        </div>
      </div>
    )
  }

  const toggleLetter = (letter) => {
    if (isolatedLetter === letter) {
      // If clicking the isolated letter, show all again
      setIsolatedLetter(null)
      setVisibleLetters({
        A: true, B: true, C: true, D: true, E: true, F: true, G: true
      })
    } else {
      // Isolate this letter
      setIsolatedLetter(letter)
      setVisibleLetters({
        A: letter === 'A',
        B: letter === 'B',
        C: letter === 'C',
        D: letter === 'D',
        E: letter === 'E',
        F: letter === 'F',
        G: letter === 'G'
      })
    }
  }

  const toggleAllLetters = () => {
    const allVisible = Object.values(visibleLetters).every(v => v)
    if (allVisible) {
      // Hide all
      setVisibleLetters({
        A: false, B: false, C: false, D: false, E: false, F: false, G: false
      })
    } else {
      // Show all
      setIsolatedLetter(null)
      setVisibleLetters({
        A: true, B: true, C: true, D: true, E: true, F: true, G: true
      })
    }
  }

  const resetZoom = () => {
    setXDomain(null)
    setIsPanning(false)
    setPanStart(null)
  }

  // Calculate data boundaries
  const dataMin = trendData?.data_points[0]?.position || 0
  const dataMax = trendData?.data_points[trendData.data_points.length - 1]?.position || 1
  const currentDomain = xDomain || [dataMin, dataMax]

  // Mouse wheel zoom handler
  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const handleWheel = (e) => {
      // Only zoom with Ctrl key
      if (!e.ctrlKey) return
      
      e.preventDefault()
      
      // Get mouse position relative to chart
      const rect = container.getBoundingClientRect()
      const mouseX = e.clientX - rect.left
      const chartWidth = rect.width
      const mouseRatio = mouseX / chartWidth // 0 to 1
      
      // Calculate zoom factor
      const zoomFactor = e.deltaY > 0 ? 1.1 : 0.9 // zoom out : zoom in
      
      const [currentMin, currentMax] = currentDomain
      const currentRange = currentMax - currentMin
      const newRange = currentRange * zoomFactor
      
      // Zoom toward cursor position
      const mousePos = currentMin + (currentRange * mouseRatio)
      const newMin = mousePos - (newRange * mouseRatio)
      const newMax = mousePos + (newRange * (1 - mouseRatio))
      
      // Clamp to data boundaries
      const clampedMin = Math.max(dataMin, newMin)
      const clampedMax = Math.min(dataMax, newMax)
      
      setXDomain([clampedMin, clampedMax])
    }
    
    container.addEventListener('wheel', handleWheel, { passive: false })
    return () => container.removeEventListener('wheel', handleWheel)
  }, [xDomain, dataMin, dataMax, currentDomain])

  // Click-drag pan handlers
  const handleMouseDown = (e) => {
    if (e.button !== 0) return // Left click only
    setIsPanning(true)
    setPanStart({ x: e.clientX, domain: currentDomain })
    e.preventDefault()
  }

  const handleMouseMove = (e) => {
    if (!isPanning || !panStart) return
    
    const container = containerRef.current
    if (!container) return
    
    const rect = container.getBoundingClientRect()
    const dx = e.clientX - panStart.x
    const chartWidth = rect.width
    
    const [min, max] = panStart.domain
    const range = max - min
    const shift = -(dx / chartWidth) * range // Negative for natural drag
    
    let newMin = min + shift
    let newMax = max + shift
    
    // Keep within data boundaries
    if (newMin < dataMin) {
      newMin = dataMin
      newMax = dataMin + range
    }
    if (newMax > dataMax) {
      newMax = dataMax
      newMin = dataMax - range
    }
    
    setXDomain([newMin, newMax])
  }

  const handleMouseUp = () => {
    setIsPanning(false)
    setPanStart(null)
  }

  // Prepare data with deviation areas for shading
  const enrichedData = trendData?.data_points?.map(point => {
    const enriched = { ...point }
    
    if (showShading && showBaselines && trendData.baseline_frequencies) {
      Object.keys(LETTER_COLORS).forEach(letter => {
        if (visibleLetters[letter]) {
          const freq = point[`freq_${letter}`]
          const baseline = trendData.baseline_frequencies[letter]
          
          if (freq > baseline) {
            // Above baseline - green shading
            enriched[`shade_above_${letter}`] = freq - baseline
            enriched[`shade_below_${letter}`] = 0
          } else {
            // Below baseline - red shading
            enriched[`shade_above_${letter}`] = 0
            enriched[`shade_below_${letter}`] = baseline - freq
          }
        }
      })
    }
    
    return enriched
  }) || []

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || payload.length === 0) return null

    return (
      <div className="trend-tooltip">
        <p className="tooltip-position">Draw #{payload[0].payload.position}</p>
        {payload.map((entry) => (
          <p key={entry.name} style={{ color: entry.color }}>
            {entry.name}: {entry.value.toFixed(2)}%
          </p>
        ))}
      </div>
    )
  }

  return (
    <div className="trend-chart-container">
      <div className="trend-chart-header">
        <h3>Rolling Frequency Trend</h3>
        <div className="trend-chart-info">
          <span>Window: {trendData.window_size} draws</span>
          <span>•</span>
          <span>Interval: {trendData.interval} draws</span>
          <span>•</span>
          <span>Total: {trendData.total_draws.toLocaleString()} draws</span>
        </div>
      </div>

      <div className="trend-controls">
        <div className="trend-controls-left">
          <button
            onClick={toggleAllLetters}
            className="btn-control"
          >
            {Object.values(visibleLetters).every(v => v) ? 'Hide All' : 'Show All'}
          </button>
          <label className="baseline-toggle">
            <input
              type="checkbox"
              checked={showBaselines}
              onChange={(e) => setShowBaselines(e.target.checked)}
            />
            <span>Show Baselines</span>
          </label>
          <label className="baseline-toggle">
            <input
              type="checkbox"
              checked={showShading}
              onChange={(e) => setShowShading(e.target.checked)}
              disabled={!showBaselines}
            />
            <span>Show Deviation Shading</span>
          </label>
          {xDomain && (
            <button
              onClick={resetZoom}
              className="btn-control btn-zoom-reset"
            >
              Reset Zoom
            </button>
          )}
        </div>
        
        <div className="letter-toggles">
          {Object.keys(LETTER_COLORS).map(letter => (
            <button
              key={letter}
              onClick={() => toggleLetter(letter)}
              className={`letter-toggle ${visibleLetters[letter] ? 'active' : ''} ${isolatedLetter === letter ? 'isolated' : ''}`}
              style={{
                borderColor: LETTER_COLORS[letter],
                backgroundColor: visibleLetters[letter] ? LETTER_COLORS[letter] : 'transparent',
                color: visibleLetters[letter] ? '#181A20' : LETTER_COLORS[letter]
              }}
            >
              {letter}
            </button>
          ))}
        </div>
      </div>

      <div 
        ref={containerRef}
        className={`chart-zoom-container ${isPanning ? 'panning' : ''}`}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <ResponsiveContainer width="100%" height={420}>
          <LineChart
            data={enrichedData}
            margin={{ top: 5, right: 30, left: 20, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#2B3139" />
            <XAxis
              dataKey="position"
              label={{ value: 'Draw Position', position: 'insideBottom', offset: -5, fill: '#848E9C' }}
              stroke="#848E9C"
              domain={xDomain ? [xDomain[0], xDomain[1]] : ['dataMin', 'dataMax']}
              type="number"
              allowDataOverflow={true}
              tick={{ fill: '#848E9C' }}
            />
          <YAxis
            label={{ value: 'Frequency %', angle: -90, position: 'insideLeft', fill: '#848E9C' }}
            domain={[0, 'auto']}
            stroke="#848E9C"
            tick={{ fill: '#848E9C' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            onClick={(e) => toggleLetter(e.value)}
            wrapperStyle={{ cursor: 'pointer' }}
          />

          {/* Baseline reference lines - muted colors */}
          {showBaselines && Object.keys(LETTER_COLORS).map(letter => (
            visibleLetters[letter] && (
              <ReferenceLine
                key={`baseline-${letter}`}
                y={trendData.baseline_frequencies[letter]}
                stroke={BASELINE_COLORS[letter]}
                strokeDasharray="8 4"
                strokeWidth={2}
                strokeOpacity={0.7}
                label={{
                  value: `${letter} baseline (${trendData.baseline_frequencies[letter].toFixed(1)}%)`,
                  position: 'right',
                  fill: BASELINE_COLORS[letter],
                  fontSize: 10,
                  fontWeight: 600
                }}
              />
            )
          ))}

          {/* Deviation shading areas */}
          {showShading && showBaselines && Object.keys(LETTER_COLORS).map(letter => (
            visibleLetters[letter] && [
              // Above baseline (green tint - Binance success)
              <Area
                key={`above-${letter}`}
                type="monotone"
                dataKey={`shade_above_${letter}`}
                stackId={letter}
                stroke="none"
                fill="#0ECB81"
                fillOpacity={0.12}
              />,
              // Below baseline (red tint - Binance danger)
              <Area
                key={`below-${letter}`}
                type="monotone"
                dataKey={`shade_below_${letter}`}
                stackId={letter}
                stroke="none"
                fill="#F6465D"
                fillOpacity={0.12}
              />
            ]
          ))}

          {/* Letter frequency lines */}
          {Object.keys(LETTER_COLORS).map(letter => (
            visibleLetters[letter] && (
              <Line
                key={letter}
                type="monotone"
                dataKey={`freq_${letter}`}
                name={letter}
                stroke={LETTER_COLORS[letter]}
                strokeWidth={isolatedLetter === letter ? 3 : 2}
                dot={false}
                activeDot={{ r: 6 }}
              />
            )
          ))}
        </LineChart>
      </ResponsiveContainer>
      
      <div className="zoom-instructions">
        Ctrl+Scroll to zoom • Click & drag to pan
      </div>
    </div>

      <div className="trend-disclaimer">
        <span className="disclaimer-icon">ℹ️</span>
        <span>
          Shows recent frequency vs historical baseline over time. This is not a predictive pattern — 
          draws are statistically independent, so chart shapes don't forecast future draws.
        </span>
      </div>
    </div>
  )
}

export default RollingFrequencyChart
