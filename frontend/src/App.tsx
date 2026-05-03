import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Identification from './pages/Identification'
import TurtleProfile from './pages/TurtleProfile'
import Login from './pages/Login'
import Gallery from './pages/Gallery'
import './styles/globals.css'
import './styles/globals.css'

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/identification" element={<ProtectedRoute><Identification /></ProtectedRoute>} />
        <Route path="/gallery" element={<ProtectedRoute><Gallery /></ProtectedRoute>} />
        <Route path="/turtle/:id" element={<ProtectedRoute><TurtleProfile /></ProtectedRoute>} />
      </Routes>
    </Router>
  )
}

export default App
