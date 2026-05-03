import React, { useState } from 'react'
import { MapPin, Calendar, User, FileText } from 'lucide-react'
import type { Sighting } from '../../types/turtle'

interface SightingHistoryProps {
  sightings: Sighting[]
}

const SightingHistory: React.FC<SightingHistoryProps> = ({ sightings }) => {
  const [page, setPage] = useState(1)
  const itemsPerPage = 5
  const totalPages = Math.ceil(sightings.length / itemsPerPage)
  const startIdx = (page - 1) * itemsPerPage
  const displayedSightings = sightings.slice(startIdx, startIdx + itemsPerPage)

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6">
      <h3 className="text-lg font-semibold text-slate-900 mb-6">Avistama Geçmişi</h3>

      {sightings.length === 0 ? (
        <div className="text-center py-8 text-slate-500">
          <p>Henüz avistama kaydı yok</p>
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {displayedSightings.map((sighting, idx) => (
              <div
                key={sighting.id}
                className="border border-slate-200 rounded-lg p-4 hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 space-y-3">
                    {/* Timeline number */}
                    <div className="flex items-center gap-2">
                      <span className="inline-flex items-center justify-center w-6 h-6 bg-gradient-to-br from-teal-500 to-blue-600 rounded-full text-white text-xs font-bold">
                        {startIdx + idx + 1}
                      </span>
                      <span className="text-sm font-medium text-slate-600">
                        {formatDate(sighting.dateSighted)}
                      </span>
                    </div>

                    {/* Location */}
                    <div className="flex items-center gap-2 text-slate-700">
                      <MapPin className="w-4 h-4 text-teal-500 flex-shrink-0" />
                      <span className="font-medium">{sighting.location}</span>
                    </div>

                    {/* Observer */}
                    <div className="flex items-center gap-2 text-slate-600">
                      <User className="w-4 h-4 text-slate-400 flex-shrink-0" />
                      <span className="text-sm">{sighting.observerName}</span>
                    </div>

                    {/* Conditions */}
                    {(sighting.waterTemperature || sighting.weather || sighting.waterClarity) && (
                      <div className="grid grid-cols-3 gap-2 text-xs">
                        {sighting.waterTemperature && (
                          <div className="bg-blue-50 rounded p-2 border border-blue-200">
                            <p className="text-slate-600">Su Sıcaklığı</p>
                            <p className="font-semibold text-blue-600">{sighting.waterTemperature}°C</p>
                          </div>
                        )}
                        {sighting.weather && (
                          <div className="bg-amber-50 rounded p-2 border border-amber-200">
                            <p className="text-slate-600">Hava</p>
                            <p className="font-semibold text-amber-600">{sighting.weather}</p>
                          </div>
                        )}
                        {sighting.waterClarity && (
                          <div className="bg-teal-50 rounded p-2 border border-teal-200">
                            <p className="text-slate-600">Su Saydamlığı</p>
                            <p className="font-semibold text-teal-600">{sighting.waterClarity}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Notes */}
                    {sighting.notes && (
                      <div className="flex gap-2 text-sm bg-slate-50 rounded p-3">
                        <FileText className="w-4 h-4 text-slate-400 flex-shrink-0 mt-0.5" />
                        <p className="text-slate-700">{sighting.notes}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-between border-t border-slate-200 pt-4">
              <span className="text-sm text-slate-600">
                Sayfa {page} / {totalPages}
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="px-3 py-2 text-sm border border-slate-300 rounded hover:bg-slate-50 disabled:opacity-50 transition-colors"
                >
                  ← Önceki
                </button>
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="px-3 py-2 text-sm border border-slate-300 rounded hover:bg-slate-50 disabled:opacity-50 transition-colors"
                >
                  Sonraki →
                </button>
              </div>
            </div>
          )}

          {/* Total count */}
          <div className="mt-4 text-xs text-slate-500 text-center">
            Toplam {sightings.length} avistama kaydı
          </div>
        </>
      )}
    </div>
  )
}

export default SightingHistory
