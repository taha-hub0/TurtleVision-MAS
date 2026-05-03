import React from 'react'
import { Link } from 'lucide-react'
import type { Turtle } from '../../types/turtle'

interface RelatedTurtlesProps {
  turtles: Array<{ turtle: Turtle; similarity: number }>
  onSelect?: (turtleId: string) => void
}

const speciesLabels: Record<string, string> = {
  GREEN_TURTLE: 'Yeşil Kaplumbağa',
  LOGGERHEAD: 'Sarı Başlı Kaplumbağa',
  LEATHERBACK: 'Deri Kaplumbağa',
  HAWKSBILL: 'Şahin Kaplumbağa',
}

const getSimilarityColor = (score: number) => {
  if (score >= 0.9) return 'bg-green-100 text-green-700'
  if (score >= 0.8) return 'bg-yellow-100 text-yellow-700'
  return 'bg-orange-100 text-orange-700'
}

const getSimilarityBarColor = (score: number) => {
  if (score >= 0.9) return 'bg-green-500'
  if (score >= 0.8) return 'bg-yellow-500'
  return 'bg-orange-500'
}

const RelatedTurtles: React.FC<RelatedTurtlesProps> = ({ turtles, onSelect }) => {
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6">
      <h3 className="text-lg font-semibold text-slate-900 mb-6">Benzer Kaplumbağalar</h3>

      {turtles.length === 0 ? (
        <div className="text-center py-8 text-slate-500">
          <p>Benzer kaplumbağa bulunamadı</p>
        </div>
      ) : (
        <div className="space-y-4">
          {turtles.map((item, idx) => (
            <div
              key={item.turtle.id}
              onClick={() => onSelect?.(item.turtle.id)}
              className={`border border-slate-200 rounded-lg p-4 transition-all ${onSelect ? 'cursor-pointer hover:border-teal-400 hover:shadow-md' : ''
                }`}
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="inline-flex items-center justify-center w-6 h-6 bg-gradient-to-br from-teal-500 to-blue-600 rounded-full text-white text-xs font-bold">
                      {idx + 1}
                    </span>
                    <h4 className="font-semibold text-slate-900">
                      {speciesLabels[item.turtle.species] || item.turtle.species}
                    </h4>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">ID: {item.turtle.id}</p>
                </div>

                {/* Similarity Badge */}
                <div
                  className={`flex flex-col items-end gap-1 px-3 py-2 rounded-lg ${getSimilarityColor(item.similarity)}`}
                >
                  <span className="text-lg font-bold">{(item.similarity * 100).toFixed(0)}%</span>
                  <span className="text-xs">Benzerlik</span>
                </div>
              </div>

              {/* Similarity Bar */}
              <div className="mb-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-slate-600">Eşleşme Skoru</span>
                  <span className="text-xs font-medium text-slate-700">{item.similarity.toFixed(3)}</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${getSimilarityBarColor(item.similarity)}`}
                    style={{ width: `${item.similarity * 100}%` }}
                  />
                </div>
              </div>

              {/* Details */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                {item.turtle.measurements?.shell_length_cm && (
                  <div className="bg-slate-50 rounded p-2">
                    <p className="text-slate-600">Karapaks</p>
                    <p className="font-semibold text-slate-900">{item.turtle.measurements.shell_length_cm} cm</p>
                  </div>
                )}
                {item.turtle.sightings && (
                  <div className="bg-slate-50 rounded p-2">
                    <p className="text-slate-600">Avistamalar</p>
                    <p className="font-semibold text-slate-900">{item.turtle.sightings.length}</p>
                  </div>
                )}
              </div>

              {/* Click hint */}
              {onSelect && (
                <div className="mt-3 flex items-center gap-1 text-teal-600 text-xs font-medium">
                  <Link className="w-3 h-3" />
                  Profili görüntüle
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default RelatedTurtles
