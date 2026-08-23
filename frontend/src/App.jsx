import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import RecordsManagement from './pages/RecordsManagement'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/records" element={<RecordsManagement />} />
      </Routes>
    </Router>
  )
}

export default App
