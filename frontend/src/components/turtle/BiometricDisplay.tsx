import React, { useState } from 'react'
import { Copy, Check } from 'lucide-react'

interface BiometricDisplayProps {
  code: string
  vector: number[]
}

const BiometricDisplay: React.FC<BiometricDisplayProps> = ({ code, vector }) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const displayVector = vector.slice(0, 10)
  const remaining = vector.length - 10

  return (
    <div className="bg-gradient-to-br from-blue-50 to-teal-50 rounded-lg border border-blue-200 p-6">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-3xl">🧬</span>
        <h3 className="text-lg font-semibold text-slate-900">Biometrik Kod</h3>
      </div>

      <div className="space-y-4">
        {/* Code Display */}
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <p className="text-xs text-slate-500 mb-2">DNA Kodu</p>
          <div className="flex items-center justify-between gap-3">
            <code className="text-sm font-mono text-slate-900 break-all">{code}</code>
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-white bg-teal-500 rounded hover:bg-teal-600 transition-colors flex-shrink-0"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4" />
                  Kopyalandı
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Kopyala
                </>
              )}
            </button>
          </div>
        </div>

        {/* Vector Display */}
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <p className="text-xs text-slate-500 mb-3">Biometrik Vektör (İlk 10 değer)</p>
          <div className="grid grid-cols-5 gap-2">
            {displayVector.map((val, idx) => (
              <div key={idx} className="bg-gradient-to-br from-teal-100 to-blue-100 rounded p-2 text-center">
                <p className="text-xs font-semibold text-teal-700">{val.toFixed(2)}</p>
              </div>
            ))}
          </div>
          {remaining > 0 && (
            <p className="text-xs text-slate-500 mt-2">
              +{remaining} değer daha ({vector.length} toplam)
            </p>
          )}
        </div>

        {/* Visual Representation */}
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <p className="text-xs text-slate-500 mb-3">Görsel Temsil</p>
          <div className="flex gap-1">
            {code.split('').map((bit, idx) => (
              <div
                key={idx}
                className={`h-8 flex-1 rounded transition-colors ${bit === '1' ? 'bg-gradient-to-t from-teal-400 to-teal-300' : 'bg-slate-200'
                  }`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default BiometricDisplay
