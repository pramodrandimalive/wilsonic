import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import './Dashboard.css'
import RankedList from '../components/RankedList'
import ManualEntryForm from '../components/ManualEntryForm'
import HistoryTable from '../components/HistoryTable'
import DriftIndicator from '../components/DriftIndicator'
import WindowSizeSelector from '../components/WindowSizeSelector'
import LetterTrendCards from '../components/LetterTrendCards'
import RollingFrequencyChart from '../components/RollingFrequencyChart'

// Use environment variable for API URL, fallback to localhost for development
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function Dashboard() {
  const [ranking, setRanking] = useState([])
  const [recentDraws, setRecentDraws] = useState([])
  const [driftStatus, setDriftStatus] = useState(null)
  const [totalDraws, setTotalDraws] = useState(0)
  const [windowSize, setWindowSize] = useState(5000)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Trend chart state
  const [showTrendChart, setShowTrendChart] = useState(false)
  const [trendData, setTrendData] = useState(null)
  const [trendLoading, setTrendLoading] = useState(false)

  // Fetch trend data
  const fetchTrendData = async () => {
    try {
      setTrendLoading(true)
      const response = await fetch(`${API_BASE}/stats/rolling-trend?window_size=${windowSize}&interval=500`)
      if (!response.ok) throw new Error('Failed to fetch trend data')
      const data = await response.json()
      setTrendData(data)
    } catch (err) {
      console.error('Error fetching trend data:', err)
      setTrendData({ data_points: [], message: 'Failed to load trend data' })
    } finally {
      setTrendLoading(false)
    }
  }

  // Fetch all data
  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch ranking
      const rankingRes = await fetch(`${API_BASE}/stats/ranking`)
      if (!rankingRes.ok) throw new Error('Failed to fetch ranking')
      const rankingData = await rankingRes.json()
      setRanking(rankingData.ranking)
      setTotalDraws(rankingData.total_draws)

      // Fetch recent draws
      const drawsRes = await fetch(`${API_BASE}/draws?page=1&page_size=10`)
      if (!drawsRes.ok) throw new Error('Failed to fetch draws')
      const drawsData = await drawsRes.json()
      setRecentDraws(drawsData.draws)

      // Fetch drift status
      const driftRes = await fetch(`${API_BASE}/stats/drift?window_size=${windowSize}`)
      if (!driftRes.ok) throw new Error('Failed to fetch drift')
      const driftData = await driftRes.json()
      setDriftStatus(driftData)

    } catch (err) {
      setError(err.message)
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  // Fetch data on mount and set up auto-refresh
  useEffect(() => {
    fetchData()
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000)
    
    return () => clearInterval(interval)
  }, [windowSize])  // Re-fetch when window size changes

  // Fetch trend data when chart is toggled on or window size changes
  useEffect(() => {
    if (showTrendChart) {
      fetchTrendData()
    }
  }, [showTrendChart, windowSize])

  // Handle new draw submission
  const handleDrawSubmitted = () => {
    // Refresh all data after new draw
    fetchData()
    if (showTrendChart) {
      fetchTrendData()
    }
  }

  // Toggle trend chart
  const handleToggleTrendChart = () => {
    setShowTrendChart(prev => !prev)
  }

  if (loading && ranking.length === 0) {
    return (
      <div className="app">
        <div className="container">
          <div className="loading">Loading Wilsonic dashboard...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <div>
            <h1>Wilsonic</h1>
            <p className="subtitle">Lottery Prediction Indicator System</p>
            <p className="disclaimer">
              This is an indicator system, not a prediction oracle. Based on {totalDraws.toLocaleString()} historical draws.
            </p>
          </div>
          <div className="header-nav">
            <Link to="/records" className="nav-link">
              Manage Records
            </Link>
          </div>
        </header>

        {error && (
          <div className="error-banner">
            <strong>Error:</strong> {error}
          </div>
        )}

        <div className="status-grid">
          <DriftIndicator driftStatus={driftStatus} />
          <WindowSizeSelector value={windowSize} onChange={setWindowSize} />
        </div>

        {/* Temporarily hidden - Per-Letter Trends */}
        {/* <LetterTrendCards driftStatus={driftStatus} /> */}

        {/* Temporarily hidden - Trend Chart Toggle */}
        {/* <div className="trend-chart-toggle-section">
          <label className="trend-toggle-switch">
            <input
              type="checkbox"
              checked={showTrendChart}
              onChange={handleToggleTrendChart}
            />
            <span className="toggle-slider"></span>
            <span className="toggle-label">Show Rolling Frequency Trend Chart</span>
          </label>
        </div> */}

        {/* Temporarily hidden - Trend Chart */}
        {/* {showTrendChart && (
          trendLoading ? (
            <div className="trend-loading">Loading trend data...</div>
          ) : (
            <RollingFrequencyChart trendData={trendData} />
          )
        )} */}

        <div className="main-content">
          <div className="left-panel">
            <ManualEntryForm onDrawSubmitted={handleDrawSubmitted} apiBase={API_BASE} />
            <HistoryTable draws={recentDraws} />
          </div>

          <div className="right-panel">
            <RankedList ranking={ranking} />
          </div>
        </div>

        <footer className="footer">
          <p>Letters ranked by observed frequency. Confidence intervals show statistical uncertainty.</p>
          <p>Auto-refreshes every 30 seconds • No gap-based/"overdue" logic</p>
        </footer>
      </div>
    </div>
  )
}

export default Dashboard
