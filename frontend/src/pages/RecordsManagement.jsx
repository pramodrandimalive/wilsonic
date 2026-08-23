import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import './RecordsManagement.css'

// Use environment variable for API URL, fallback to localhost for development
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function RecordsManagement() {
  const [draws, setDraws] = useState([])
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(25)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [letterFilter, setLetterFilter] = useState('')
  const [sourceFilter, setSourceFilter] = useState('')
  const [sortOrder, setSortOrder] = useState('newest')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [editingId, setEditingId] = useState(null)
  const [editLetter, setEditLetter] = useState('')
  const [editTimestamp, setEditTimestamp] = useState('')

  // Fetch draws with filters
  const fetchDraws = async () => {
    try {
      setLoading(true)
      setError(null)

      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        sort: sortOrder
      })

      if (letterFilter) params.append('letter', letterFilter)
      if (sourceFilter) params.append('source', sourceFilter)

      const response = await fetch(`${API_BASE}/draws?${params}`)
      if (!response.ok) throw new Error('Failed to fetch draws')
      
      const data = await response.json()
      setDraws(data.draws)
      setTotal(data.total)
      setTotalPages(data.total_pages)
    } catch (err) {
      setError(err.message)
      console.error('Error fetching draws:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDraws()
  }, [page, pageSize, letterFilter, sourceFilter, sortOrder])

  // Start editing a draw
  const startEdit = (draw) => {
    setEditingId(draw.id)
    setEditLetter(draw.letter)
    // Convert ISO timestamp to input format (YYYY-MM-DDTHH:MM)
    const timestamp = new Date(draw.timestamp)
    const localTimestamp = new Date(timestamp.getTime() - timestamp.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 16)
    setEditTimestamp(localTimestamp)
  }

  // Cancel editing
  const cancelEdit = () => {
    setEditingId(null)
    setEditLetter('')
    setEditTimestamp('')
  }

  // Save edited draw
  const saveEdit = async (id) => {
    try {
      // Convert local timestamp to ISO format
      const timestamp = new Date(editTimestamp).toISOString()
      
      const response = await fetch(`${API_BASE}/draws/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          letter: editLetter,
          timestamp: timestamp
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to update draw')
      }

      // Refresh the list
      await fetchDraws()
      cancelEdit()
    } catch (err) {
      alert(`Error updating draw: ${err.message}`)
      console.error('Error updating draw:', err)
    }
  }

  // Delete a draw
  const deleteDraw = async (id, letter) => {
    if (!confirm(`Are you sure you want to delete draw #${id} (${letter})? This will affect the statistics.`)) {
      return
    }

    try {
      const response = await fetch(`${API_BASE}/draws/${id}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to delete draw')
      }

      // Refresh the list
      await fetchDraws()
    } catch (err) {
      alert(`Error deleting draw: ${err.message}`)
      console.error('Error deleting draw:', err)
    }
  }

  // Format timestamp for display
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <div className="records-management">
      <div className="records-header">
        <div className="records-title-section">
          <Link to="/" className="back-link">← Back to Dashboard</Link>
          <h1>Records Management</h1>
          <p className="records-count">{total} total records</p>
        </div>
        
        <div className="warning-banner">
          <span className="warning-icon">⚠️</span>
          <span>Editing or deleting records will change statistical calculations across the app.</span>
        </div>
      </div>

      <div className="controls-section">
        <div className="filters">
          <div className="filter-group">
            <label htmlFor="letter-filter">Letter:</label>
            <select
              id="letter-filter"
              value={letterFilter}
              onChange={(e) => {
                setLetterFilter(e.target.value)
                setPage(1) // Reset to first page on filter change
              }}
            >
              <option value="">All</option>
              <option value="A">A</option>
              <option value="B">B</option>
              <option value="C">C</option>
              <option value="D">D</option>
              <option value="E">E</option>
              <option value="F">F</option>
              <option value="G">G</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="source-filter">Source:</label>
            <select
              id="source-filter"
              value={sourceFilter}
              onChange={(e) => {
                setSourceFilter(e.target.value)
                setPage(1)
              }}
            >
              <option value="">All</option>
              <option value="manual">Manual</option>
              <option value="historical_import">Historical Import</option>
              <option value="scraper">Scraper</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="sort-order">Sort:</label>
            <select
              id="sort-order"
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value)}
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="page-size">Per Page:</label>
            <select
              id="page-size"
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value))
                setPage(1)
              }}
            >
              <option value="25">25</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>
        </div>
      </div>

      {loading && <div className="loading">Loading records...</div>}
      {error && <div className="error">Error: {error}</div>}

      {!loading && !error && (
        <>
          <div className="table-container">
            <table className="records-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Letter</th>
                  <th>Timestamp</th>
                  <th>Source</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {draws.map((draw) => (
                  <tr key={draw.id}>
                    <td>{draw.id}</td>
                    <td>
                      {editingId === draw.id ? (
                        <select
                          value={editLetter}
                          onChange={(e) => setEditLetter(e.target.value)}
                          className="edit-select"
                        >
                          <option value="A">A</option>
                          <option value="B">B</option>
                          <option value="C">C</option>
                          <option value="D">D</option>
                          <option value="E">E</option>
                          <option value="F">F</option>
                          <option value="G">G</option>
                        </select>
                      ) : (
                        <span className="letter-badge">{draw.letter}</span>
                      )}
                    </td>
                    <td>
                      {editingId === draw.id ? (
                        <input
                          type="datetime-local"
                          value={editTimestamp}
                          onChange={(e) => setEditTimestamp(e.target.value)}
                          className="edit-input"
                        />
                      ) : (
                        formatTimestamp(draw.timestamp)
                      )}
                    </td>
                    <td>
                      <span className={`source-badge source-${draw.source}`}>
                        {draw.source}
                      </span>
                    </td>
                    <td>
                      {editingId === draw.id ? (
                        <div className="action-buttons">
                          <button
                            onClick={() => saveEdit(draw.id)}
                            className="btn-save"
                          >
                            Save
                          </button>
                          <button
                            onClick={cancelEdit}
                            className="btn-cancel"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <div className="action-buttons">
                          <button
                            onClick={() => startEdit(draw)}
                            className="btn-edit"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => deleteDraw(draw.id, draw.letter)}
                            className="btn-delete"
                          >
                            Delete
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="btn-pagination"
            >
              Previous
            </button>
            <span className="page-info">
              Page {page} of {totalPages} ({total} total)
            </span>
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page === totalPages}
              className="btn-pagination"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  )
}

export default RecordsManagement
