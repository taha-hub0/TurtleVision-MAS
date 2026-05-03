import React from 'react'
import type { Turtle } from '../types/turtle'
import type { ComparisonResult } from '../api/services/turtleService'

interface ComparisonTableProps {
  turtle1: Turtle
  turtle2: Turtle
  comparison: ComparisonResult
}

const speciesLabels: Record<string, string> = {
  GREEN_TURTLE: 'Yeşil Kaplumbağa',
  LOGGERHEAD: 'Sarı Başlı Kaplumbağa',
  LEATHERBACK: 'Deri Kaplumbağa',
  HAWKSBILL: 'Şahin Kaplumbağa',
}

const ComparisonTable: React.FC<ComparisonTableProps> = ({ turtle1, turtle2, comparison }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const rows = [
    {
      label: 'Tür',
      value1: speciesLabels[turtle1.species] || turtle1.species,
      value2: speciesLabels[turtle2.species] || turtle2.species,
      match: turtle1.species === turtle2.species,
    },
    {
      label: 'Sistem ID',
      value1: turtle1.id,
      value2: turtle2.id,
      match: turtle1.id === turtle2.id,
    },
    {
      label: 'Biometrik Kod',
      value1: turtle1.biometric_code.substring(0, 10) + '...',
      value2: turtle2.biometric_code.substring(0, 10) + '...',
      match: turtle1.biometric_code === turtle2.biometric_code,
    },
    {
      label: 'Karapaks Uzunluğu',
      value1: turtle1.measurements?.shell_length_cm ? `${turtle1.measurements.shell_length_cm} cm` : '-',
      value2: turtle2.measurements?.shell_length_cm ? `${turtle2.measurements.shell_length_cm} cm` : '-',
      match:
        turtle1.measurements && turtle2.measurements
          ? Math.abs(turtle1.measurements.shell_length_cm - turtle2.measurements.shell_length_cm) < 5
          : false,
    },
    {
      label: 'Ağırlık',
      value1: turtle1.measurements?.weight_kg ? `${turtle1.measurements.weight_kg} kg` : '-',
      value2: turtle2.measurements?.weight_kg ? `${turtle2.measurements.weight_kg} kg` : '-',
      match:
        turtle1.measurements && turtle2.measurements
          ? Math.abs(turtle1.measurements.weight_kg - turtle2.measurements.weight_kg) < 5
          : false,
    },
    {
      label: 'Sağlık Durumu',
      value1: turtle1.health?.status || '-',
      value2: turtle2.health?.status || '-',
      match: turtle1.health?.status === turtle2.health?.status,
    },
    {
      label: 'Toplam Avistama',
      value1: `${turtle1.sightings?.length || 0} kez`,
      value2: `${turtle2.sightings?.length || 0} kez`,
      match: false,
    },
    {
      label: 'Son Görülüş',
      value1: turtle1.sightings?.[0] ? formatDate(turtle1.sightings[0].dateSighted) : '-',
      value2: turtle2.sightings?.[0] ? formatDate(turtle2.sightings[0].dateSighted) : '-',
      match: false,
    },
  ]

  return (
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              <th className="text-left px-6 py-3 font-semibold text-slate-900">Özellik</th>
              <th className="text-left px-6 py-3 font-semibold text-slate-900">Kaplumbağa 1</th>
              <th className="text-left px-6 py-3 font-semibold text-slate-900">Kaplumbağa 2</th>
              <th className="text-center px-6 py-3 font-semibold text-slate-900">Uyum</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr
                key={idx}
                className={`border-b border-slate-200 hover:bg-slate-50 transition-colors ${idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'
                  }`}
              >
                <td className="px-6 py-4 font-medium text-slate-900">{row.label}</td>
                <td className="px-6 py-4 text-slate-700">{row.value1}</td>
                <td className="px-6 py-4 text-slate-700">{row.value2}</td>
                <td className="px-6 py-4 text-center">
                  {row.match ? (
                    <span className="inline-flex items-center justify-center w-6 h-6 bg-green-100 rounded-full">
                      <span className="text-green-600 font-bold">✓</span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center justify-center w-6 h-6 bg-slate-200 rounded-full">
                      <span className="text-slate-600 text-sm">−</span>
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary */}
      <div className="bg-slate-50 px-6 py-4 border-t border-slate-200">
        <p className="text-sm text-slate-700">
          <span className="font-semibold">Özet:</span> Sistem {comparison.verdict === 'SAME' ? '✅ bu iki kaplumbağayı aynı birey olarak tanımladı' :
            comparison.verdict === 'LIKELY_SAME' ? '⚠️ muhtemelen aynı birey olabileceğini belirtti' :
              comparison.verdict === 'UNCERTAIN' ? '❓ belirsiz sonuç verdi, manuel kontrol önerilir' :
                '❌ farklı bireyler olduğunu belirledi'}.
        </p>
      </div>
    </div>
  )
}

export default ComparisonTable
