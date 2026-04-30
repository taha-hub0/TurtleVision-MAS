import React from 'react'
import { useLocation } from 'react-router-dom'
import { Turtle } from 'lucide-react'

const Header: React.FC = () => {
  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-teal-500 to-blue-600 rounded-lg flex items-center justify-center shadow-md">
            <Turtle className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-teal-600 to-blue-600 bg-clip-text text-transparent">
              TurtleVision
            </h1>
            <p className="text-xs text-slate-500">Non-Invasive ID System</p>
          </div>
        </div>
      </div>
    </header>
  )
}

const Sidebar: React.FC = () => {
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path || location.pathname.startsWith(path)

  const navItems = [
    { path: '/dashboard', label: '📊 Dashboard' },
    { path: '/identification', label: '🔍 Yeni Analiz' },
  ]

  return (
    <aside className="w-64 bg-white border-r border-slate-200 p-6 overflow-y-auto">
      <div className="space-y-8">
        <nav className="space-y-2">
          {navItems.map((item) => (
            <a
              key={item.path}
              href={item.path}
              className={`block px-4 py-2.5 rounded-lg font-medium transition-all ${
                isActive(item.path)
                  ? 'bg-teal-50 text-teal-600 shadow-sm'
                  : 'text-slate-700 hover:bg-slate-50'
              }`}
            >
              {item.label}
            </a>
          ))}
        </nav>

        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-600 px-4">Sistem Durumu</h3>
          <div className="bg-blue-50 rounded-lg p-3 space-y-2 text-xs border border-blue-100">
            {[
              { label: 'Backend', status: 'Aktif' },
              { label: 'Görüntü Analiz', status: 'Aktif' },
              { label: 'Veritabanı', status: 'Aktif' },
            ].map((item) => (
              <div key={item.label} className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span className="text-slate-700">
                  {item.label}: <strong>{item.status}</strong>
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="border-t border-slate-200 pt-6">
          <h3 className="text-sm font-semibold text-slate-600 mb-3">Sistem Hakkında</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            <strong>Non-Invasive</strong> deniz kaplumbağası tanımlama sistemi. Zararsız, hızlı ve güvenilir.
          </p>
        </div>
      </div>
    </aside>
  )
}

interface MainLayoutProps {
  children: React.ReactNode
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

export default MainLayout
