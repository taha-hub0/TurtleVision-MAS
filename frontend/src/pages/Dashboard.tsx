import React, { useState, useEffect } from 'react'
import { Plus, Upload, TrendingUp, Database, Activity, ShieldCheck } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import MainLayout from '../layouts/MainLayout'
import StatCard from '../components/common/StatCard'

const Dashboard: React.FC = () => {
  const navigate = useNavigate()
  const [totalTurtles, setTotalTurtles] = useState<number | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('http://localhost:5000/api/gallery')
        const data = await res.json()
        if (data.success) {
          setTotalTurtles(data.images.length)
        }
      } catch (e) {
        console.error('Veritabanı bilgileri alınamadı')
      }
    }
    fetchStats()
  }, [])

  const statCards = [
    {
      icon: <Database className="w-6 h-6 text-white" />,
      label: 'Kayıtlı Kaplumbağa',
      value: totalTurtles !== null ? totalTurtles.toString() : '...',
      color: 'bg-blue-500',
    },
    {
      icon: <Upload className="w-6 h-6 text-white" />,
      label: 'Bugünkü Analiz',
      value: '12',
      color: 'bg-teal-500',
    },
    {
      icon: <ShieldCheck className="w-6 h-6 text-white" />,
      label: 'Aktif Sensör/Ajan',
      value: '4',
      color: 'bg-indigo-500',
    },
  ]

  const recentAnalyses = [
    { id: 'turtle-001', species: 'Yeşil', location: 'Dalyan Plajı', similarity: 95 },
    { id: 'turtle-002', species: 'Loggerhead', location: 'Ölüdeniz', similarity: 92 },
    { id: 'turtle-003', species: 'Leather', location: 'Patara Plajı', similarity: 88 },
  ]

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-slate-900">Dashboard</h1>
            <p className="text-slate-600 mt-1">Deniz kaplumbağası izleme sistemi genel bakışı</p>
          </div>
          <a
            href="/identification"
            className="flex items-center gap-2 bg-gradient-to-r from-teal-500 to-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-shadow active:scale-95"
          >
            <Plus className="w-5 h-5" />
            Yeni Analiz
          </a>
        </div>

        {/* Statistics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {statCards.map((card) => (
            <StatCard key={card.label} {...card} />
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Charts Area */}
          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <h2 className="text-xl font-semibold text-slate-900 mb-6 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-teal-600"/> Tespit Edilen Tür Dağılımı
            </h2>
            <div className="flex items-center justify-center gap-8 py-4">
              {/* Fake CSS Pie Chart */}
              <div 
                className="w-40 h-40 rounded-full"
                style={{
                  background: 'conic-gradient(#14b8a6 0% 65%, #3b82f6 65% 90%, #f59e0b 90% 100%)',
                  boxShadow: 'inset 0 0 0 16px white, 0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
              />
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-teal-500"></div>
                  <span className="text-sm font-medium text-slate-700">Yeşil Kaplumbağa (%65)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                  <span className="text-sm font-medium text-slate-700">Caretta Caretta (%25)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-amber-500"></div>
                  <span className="text-sm font-medium text-slate-700">Deri Sırtlı (%10)</span>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Analysis */}
          <div className="bg-white rounded-lg border border-slate-200 p-6 flex flex-col h-full">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-slate-900">Son Yapılan Analizler</h2>
              <span className="text-xs font-semibold text-teal-600 bg-teal-50 px-2 py-1 rounded-full">CANLI</span>
            </div>
            <div className="space-y-3 flex-1">
              {recentAnalyses.map((analysis) => (
                <div
                  key={analysis.id}
                  className="flex items-center justify-between p-4 border border-slate-100 rounded-lg bg-slate-50 hover:bg-teal-50 hover:border-teal-200 transition-all cursor-pointer"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-xs font-bold text-slate-500 shadow-sm border border-slate-200">
                      ID
                    </div>
                    <div className="text-left">
                      <p className="font-semibold text-slate-900 text-sm">{analysis.species} Kaplumbağa</p>
                      <p className="text-xs text-slate-500">📍 {analysis.location}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-teal-600">{analysis.similarity}%</p>
                    <p className="text-[10px] uppercase tracking-wider text-slate-500">Benzerlik</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* System Info */}
        <div className="bg-gradient-to-r from-teal-50 to-blue-50 rounded-lg border border-teal-200 p-6">
          <h3 className="font-semibold text-slate-900 mb-4">💡 Non-Invasive Tanımlama Avantajları</h3>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-700">
            {[
              'Kaplumbağaya hiçbir zarar vermez',
              'Geleneksel markalamadan daha ekonomiktir',
              'Yüksek doğruluk ve güvenilirlik',
              'Uzun vadeli popülasyon izlemesine olanak tanır',
            ].map((item) => (
              <li key={item} className="flex gap-2">
                <span className="text-teal-600 font-bold">✓</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </MainLayout>
  )
}

export default Dashboard

