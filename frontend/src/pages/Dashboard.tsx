import React, { useState } from 'react'
import { Plus, Upload, TrendingUp, Database } from 'lucide-react'
import MainLayout from '../layouts/MainLayout'
import StatCard from '../components/common/StatCard'

const Dashboard: React.FC = () => {
  const [stats] = useState({
    totalTurtles: 247,
    recentAnalysis: 12,
    dekamerActivities: 89,
    activeMonitoring: 15,
  })

  const statCards = [
    {
      icon: <Database className="w-6 h-6 text-white" />,
      label: 'Kayıtlı Kaplumbağa',
      value: stats.totalTurtles.toString(),
      color: 'bg-blue-500',
    },
    {
      icon: <Upload className="w-6 h-6 text-white" />,
      label: 'Bugünkü Analiz',
      value: stats.recentAnalysis.toString(),
      color: 'bg-teal-500',
    },
    {
      icon: <TrendingUp className="w-6 h-6 text-white" />,
      label: 'DEKAMER Faaliyetleri',
      value: stats.dekamerActivities.toString(),
      color: 'bg-green-500',
    },
    {
      icon: <span className="text-2xl">📊</span>,
      label: 'Aktif İzleme',
      value: stats.activeMonitoring.toString(),
      color: 'bg-purple-500',
    },
  ]

  const recentAnalyses = [
    { id: 123, species: 'Yeşil', location: 'Dalyan Plajı', similarity: 95 },
    { id: 124, species: 'Loggerhead', location: 'Ölüdeniz', similarity: 92 },
    { id: 125, species: 'Leather', location: 'Patara Plajı', similarity: 88 },
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
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((card) => (
            <StatCard key={card.label} {...card} />
          ))}
        </div>

        {/* Recent Analysis */}
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <h2 className="text-xl font-semibold text-slate-900 mb-6">Son Analizler</h2>
          <div className="space-y-3">
            {recentAnalyses.map((analysis) => (
              <div
                key={analysis.id}
                className="flex items-center justify-between p-4 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-teal-200 to-blue-200 rounded-lg flex items-center justify-center text-sm font-bold text-teal-700">
                    #{analysis.id}
                  </div>
                  <div className="text-left">
                    <p className="font-medium text-slate-900">{analysis.species} Kaplumbağa</p>
                    <p className="text-sm text-slate-600">{analysis.location} • 2 saat önce</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-teal-600">{analysis.similarity}%</p>
                  <p className="text-xs text-slate-600">Benzerlik</p>
                </div>
              </div>
            ))}
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

