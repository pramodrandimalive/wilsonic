import { useState } from 'react'
import './ManualEntryForm.css'

const LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

function ManualEntryForm({ onDrawSubmitted, apiBase }) {
  const [selectedLetter, setSelectedLetter] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [message, setMessage] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!selectedLetter) {
      setMessage({ type: 'error', text: 'Please select a letter' })
      return
    }

    setSubmitting(true)
    setMessage(null)

    try {
      const response = await fetch(`${apiBase}/draws`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ letter: selectedLetter }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to submit draw')
      }

      const data = await response.json()
      setMessage({ 
        type: 'success', 
        text: `Draw ${data.letter} added successfully!` 
      })
      setSelectedLetter(null)
      
      // Call parent callback to refresh data
      if (onDrawSubmitted) {
        onDrawSubmitted()
      }

      // Clear success message after 3 seconds
      setTimeout(() => setMessage(null), 3000)

    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.message 
      })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="manual-entry-card">
      <h2>Manual Entry</h2>
      <p className="section-description">
        Select the letter that was drawn and click "Add Draw"
      </p>

      <form onSubmit={handleSubmit} className="entry-form">
        <div className="letter-buttons">
          {LETTERS.map((letter) => (
            <button
              key={letter}
              type="button"
              className={`letter-button ${selectedLetter === letter ? 'selected' : ''}`}
              onClick={() => setSelectedLetter(letter)}
              disabled={submitting}
            >
              {letter}
            </button>
          ))}
        </div>

        <button 
          type="submit" 
          className="submit-button"
          disabled={!selectedLetter || submitting}
        >
          {submitting ? 'Adding...' : 'Add Draw'}
        </button>

        {message && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}
      </form>
    </div>
  )
}

export default ManualEntryForm
