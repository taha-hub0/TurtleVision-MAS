import React from 'react'

interface StatCardProps {
  icon: React.ReactNode
  label: string
  value: string
  color: string
}

const StatCard: React.FC<StatCardProps> = ({ icon, label, value, color }) => (
  <div className="bg-white rounded-lg border border-slate-200 p-6 hover:shadow-lg transition-shadow">
    <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${color}`}>
      {icon}
    </div>
    <p className="text-sm text-slate-600 mb-1">{label}</p>
    <p className="text-3xl font-bold text-slate-900">{value}</p>
  </div>
)

export default StatCard
