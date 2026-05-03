import React from 'react'
import { Activity, Ruler, Weight, Calendar, Heart, AlertCircle } from 'lucide-react'
import type { Turtle } from '../../types/turtle'

interface TurtleStatsProps {
  turtle: Turtle
}

const speciesLabels: Record<string, string> = {
  GREEN_TURTLE: 'Yeşil Kaplumbağa',
  LOGGERHEAD: 'Sarı Başlı Kaplumbağa',
  LEATHERBACK: 'Deri Kaplumbağa',
  HAWKSBILL: 'Şahin Kaplumbağa',
}

const healthStatusColors: Record<string, string> = {
  HEALTHY: 'bg-green-50 border-green-200 text-green-700',
  WARNING: 'bg-amber-50 border-amber-200 text-amber-700',
  CRITICAL: 'bg-red-50 border-red-200 text-red-700',
}

const TurtleStats: React.FC<TurtleStatsProps> = ({ turtle }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  const sightingCount = turtle.sightings?.length || 0
  const lastSighting = turtle.sightings?.[0]
  const daysSinceLastSighting = lastSighting
    ? Math.floor((new Date().getTime() - new Date(lastSighting.dateSighted).getTime()) / (1000 * 60 * 60 * 24))
    : null

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Basic Info */}
      <div className="lg:col-span-2 space-y-4">
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-6">Temel Bilgiler</h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {/* Species */}
            <div className="flex items-start gap-3">
              <div className="flex items-center justify-center w-10 h-10 bg-blue-100 rounded-lg">
                <AlertCircle className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600">Tür</p>
                <p className="text-base font-semibold text-slate-900">
                  {speciesLabels[turtle.species] || turtle.species}
                </p>
              </div>
            </div>

            {/* ID */}
            <div className="flex items-start gap-3">
              <div className="flex items-center justify-center w-10 h-10 bg-purple-100 rounded-lg">
                <span className="text-lg">🆔</span>
              </div>
              <div>
                <p className="text-sm text-slate-600">Sistem ID</p>
                <p className="text-base font-mono font-semibold text-slate-900">{turtle.id}</p>
              </div>
            </div>

            {/* Shell Length */}
            {turtle.measurements?.shell_length_cm && (
              <div className="flex items-start gap-3">
                <div className="flex items-center justify-center w-10 h-10 bg-cyan-100 rounded-lg">
                  <Ruler className="w-5 h-5 text-cyan-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-600">Karapaks Uzunluğu</p>
                  <p className="text-base font-semibold text-slate-900">{turtle.measurements.shell_length_cm} cm</p>
                </div>
              </div>
            )}

            {/* Shell Width */}
            {turtle.measurements?.shell_width_cm && (
              <div className="flex items-start gap-3">
                <div className="flex items-center justify-center w-10 h-10 bg-cyan-100 rounded-lg">
                  <Ruler className="w-5 h-5 text-cyan-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-600">Karapaks Genişliği</p>
                  <p className="text-base font-semibold text-slate-900">{turtle.measurements.shell_width_cm} cm</p>
                </div>
              </div>
            )}

            {/* Weight */}
            {turtle.measurements?.weight_kg && (
              <div className="flex items-start gap-3">
                <div className="flex items-center justify-center w-10 h-10 bg-orange-100 rounded-lg">
                  <Weight className="w-5 h-5 text-orange-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-600">Ağırlık</p>
                  <p className="text-base font-semibold text-slate-900">{turtle.measurements.weight_kg} kg</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Dates */}
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Zaman Bilgileri</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <Calendar className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-xs text-slate-600">Veritabanı Kaydı</p>
                <p className="text-sm font-semibold text-slate-900">{formatDate(turtle.registeredAt)}</p>
              </div>
            </div>
            {lastSighting && (
              <div className="flex items-start gap-3 p-3 bg-teal-50 rounded-lg border border-teal-200">
                <Calendar className="w-5 h-5 text-teal-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs text-slate-600">Son Avistama</p>
                  <p className="text-sm font-semibold text-slate-900">{formatDate(lastSighting.dateSighted)}</p>
                  {daysSinceLastSighting !== null && (
                    <p className="text-xs text-slate-500 mt-1">{daysSinceLastSighting} gün önce</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Health & Activity */}
      <div className="space-y-4">
        {/* Health Status */}
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Sağlık Durumu</h3>

          <div
            className={`rounded-lg border p-4 ${healthStatusColors[turtle.health?.status || 'HEALTHY'] || healthStatusColors.HEALTHY}`}
          >
            <div className="flex items-center gap-2 mb-2">
              <Heart className="w-5 h-5" />
              <span className="font-semibold">
                {turtle.health?.status === 'CRITICAL'
                  ? 'Kritik'
                  : turtle.health?.status === 'WARNING'
                    ? 'Uyarı'
                    : 'Sağlıklı'}
              </span>
            </div>
            {turtle.health?.notes && <p className="text-sm">{turtle.health.notes}</p>}
          </div>
        </div>

        {/* Activity */}
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Aktivite</h3>

          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-teal-600" />
                <span className="text-sm text-slate-700">Toplam Avistamalar</span>
              </div>
              <span className="font-bold text-lg text-teal-600">{sightingCount}</span>
            </div>

            {lastSighting && (
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-blue-600" />
                  <span className="text-sm text-slate-700">Son {daysSinceLastSighting} gün</span>
                </div>
                <span className="font-bold text-lg text-blue-600">Aktif</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default TurtleStats
