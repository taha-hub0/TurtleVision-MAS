import React from 'react'
import { CheckCircle, AlertCircle, HelpCircle, XCircle } from 'lucide-react'
import type { ComparisonResult } from '../api/services/turtleService'

interface SimilarityScoreProps {
  comparison: ComparisonResult
}

const SimilarityScore: React.FC<SimilarityScoreProps> = ({ comparison }) => {
  const percentage = Math.round(comparison.similarity * 100)

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'SAME':
        return 'from-green-500 to-emerald-600'
      case 'LIKELY_SAME':
        return 'from-yellow-500 to-amber-600'
      case 'UNCERTAIN':
        return 'from-orange-500 to-red-500'
      case 'DIFFERENT':
        return 'from-red-500 to-red-700'
      default:
        return 'from-slate-500 to-slate-600'
    }
  }

  const getVerdictIcon = (verdict: string) => {
    switch (verdict) {
      case 'SAME':
        return <CheckCircle className="w-8 h-8" />
      case 'LIKELY_SAME':
        return <AlertCircle className="w-8 h-8" />
      case 'UNCERTAIN':
        return <HelpCircle className="w-8 h-8" />
      case 'DIFFERENT':
        return <XCircle className="w-8 h-8" />
      default:
        return null
    }
  }

  const getVerdictText = (verdict: string) => {
    switch (verdict) {
      case 'SAME':
        return 'AYNI KAPLUMBAĞA'
      case 'LIKELY_SAME':
        return 'MUHTEMELEN AYNI KAPLUMBAĞA'
      case 'UNCERTAIN':
        return 'BELİRSİZ - MANUEL KONTROL ÖNERİLİ'
      case 'DIFFERENT':
        return 'FARKLI BIREYLER'
      default:
        return 'ANALYSIS'
    }
  }

  const getVerdictBg = (verdict: string) => {
    switch (verdict) {
      case 'SAME':
        return 'bg-green-50 border-green-200 text-green-700'
      case 'LIKELY_SAME':
        return 'bg-amber-50 border-amber-200 text-amber-700'
      case 'UNCERTAIN':
        return 'bg-orange-50 border-orange-200 text-orange-700'
      case 'DIFFERENT':
        return 'bg-red-50 border-red-200 text-red-700'
      default:
        return 'bg-slate-50 border-slate-200 text-slate-700'
    }
  }

  return (
    <div className={`bg-gradient-to-r ${getVerdictColor(comparison.verdict)} rounded-lg p-8 text-white shadow-lg`}>
      <div className="space-y-6">
        {/* Main Score */}
        <div className="flex items-center justify-between gap-8">
          <div>
            <p className="text-white/80 text-sm font-medium mb-2">BİOMETRİK BENZERLİK</p>
            <div className="flex items-baseline gap-2">
              <span className="text-7xl font-bold">{percentage}%</span>
              <span className="text-white/70 text-lg">benzerlik</span>
            </div>
          </div>

          {/* Verdict Icon */}
          <div className="flex-shrink-0">{getVerdictIcon(comparison.verdict)}</div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-white/90">
            <span>Eşleşme Oranı</span>
            <span className="font-semibold">{percentage}%</span>
          </div>
          <div className="w-full bg-white/30 rounded-full h-3 overflow-hidden">
            <div
              className="h-full bg-white transition-all duration-500"
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>

        {/* Verdict Box */}
        <div className={`rounded-lg border p-4 ${getVerdictBg(comparison.verdict)}`}>
          <p className="font-bold text-lg">{getVerdictText(comparison.verdict)}</p>
        </div>

        {/* Score Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white/20 rounded-lg p-3">
            <p className="text-white/70 text-xs font-medium mb-1">BİOMETRİK KODLAR</p>
            <p className="text-2xl font-bold">{Math.round(comparison.biometricMatch * 100)}%</p>
          </div>
          <div className="bg-white/20 rounded-lg p-3">
            <p className="text-white/70 text-xs font-medium mb-1">ÖLÇÜMLER</p>
            <p className="text-2xl font-bold">{Math.round(comparison.measurementsMatch * 100)}%</p>
          </div>
          <div className="bg-white/20 rounded-lg p-3">
            <p className="text-white/70 text-xs font-medium mb-1">KONUM/ZAMAN</p>
            <p className="text-2xl font-bold">{comparison.timeDifference}d, {comparison.locationDistance.toFixed(0)}km</p>
          </div>
        </div>

        {/* Reasoning */}
        <div className="bg-white/20 rounded-lg p-4 space-y-2">
          <p className="text-white font-semibold text-sm">Analiz Sonuçları:</p>
          <ul className="space-y-1">
            {comparison.reasoning.map((reason, idx) => (
              <li key={idx} className="text-white/90 text-sm flex items-start gap-2">
                <span className="flex-shrink-0 mt-0.5">→</span>
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

export default SimilarityScore
