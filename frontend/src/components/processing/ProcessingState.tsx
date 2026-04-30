import React, { useEffect, useState } from 'react'
import { CheckCircle2, AlertCircle, Clock, Loader2, TrendingUp } from 'lucide-react'
import { cn } from '../../utils/cn'
import type { ProcessingStep } from '../../types/turtle'

interface ProcessingStateProps {
  steps: ProcessingStep[]
  isProcessing: boolean
  biometricCode?: string
  similarityScore?: number
  elapsedTime?: number
}

const StepIndicator: React.FC<{
  step: ProcessingStep
  isActive: boolean
  isComplete: boolean
}> = ({ step, isActive, isComplete }) => {
  const getIcon = () => {
    if (step.status === 'error') {
      return <AlertCircle className="w-5 h-5 text-red-500" />
    }
    if (isComplete) {
      return <CheckCircle2 className="w-5 h-5 text-green-500" />
    }
    if (isActive) {
      return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
    }
    return <Clock className="w-5 h-5 text-gray-400" />
  }

  return (
    <div className="flex flex-col items-center">
      <div
        className={cn(
          'w-14 h-14 rounded-full flex items-center justify-center border-2 transition-all duration-300',
          isComplete && 'bg-green-50 border-green-500',
          isActive && 'bg-blue-50 border-blue-500 ring-2 ring-blue-200',
          !isActive && !isComplete && 'bg-gray-50 border-gray-300'
        )}
      >
        {getIcon()}
      </div>
      <p className="mt-2 text-sm font-medium text-slate-700">{step.label}</p>
      {step.duration && (
        <p className="text-xs text-slate-500 mt-1">{step.duration.toFixed(1)}s</p>
      )}
      {step.error && (
        <p className="text-xs text-red-500 mt-1 text-center">{step.error}</p>
      )}
    </div>
  )
}

const ProcessingState: React.FC<ProcessingStateProps> = ({
  steps,
  isProcessing,
  biometricCode,
  similarityScore,
  elapsedTime,
}) => {
  const [displayTime, setDisplayTime] = useState(elapsedTime || 0)

  useEffect(() => {
    if (!isProcessing) return

    const interval = setInterval(() => {
      setDisplayTime((prev) => prev + 0.1)
    }, 100)

    return () => clearInterval(interval)
  }, [isProcessing])

  const activeStepIndex = steps.findIndex((s) => s.status === 'processing')
  const completedStepsCount = steps.filter((s) => s.status === 'success').length

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8">
      {/* Main Processing Timeline */}
      <div className="bg-white rounded-lg border border-slate-200 p-8">
        <h2 className="text-xl font-semibold text-slate-900 mb-8">
          🤖 Multi-Agent İşlem Süreci
        </h2>

        {/* Horizontal Timeline */}
        <div className="flex justify-between items-start mb-12">
          {steps.map((step, index) => (
            <React.Fragment key={step.id}>
              <StepIndicator
                step={step}
                isActive={step.status === 'processing'}
                isComplete={step.status === 'success'}
              />
              {index < steps.length - 1 && (
                <div
                  className={cn(
                    'flex-1 h-1 mx-4 mt-7 rounded-full transition-all duration-300',
                    index < activeStepIndex
                      ? 'bg-green-500'
                      : index === activeStepIndex
                        ? 'bg-blue-500 animate-pulse-soft'
                        : 'bg-gray-300'
                  )}
                />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden mb-4">
          <div
            className="bg-gradient-to-r from-blue-500 to-teal-500 h-full transition-all duration-300 ease-out"
            style={{ width: `${(completedStepsCount / steps.length) * 100}%` }}
          />
        </div>
        <div className="text-center text-sm text-slate-600">
          {completedStepsCount} / {steps.length} Adım Tamamlandı
        </div>
      </div>

      {/* Biometric Code Display */}
      {biometricCode && (
        <div className="bg-gradient-to-br from-teal-50 to-blue-50 rounded-lg border border-teal-200 p-6">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-2xl">🧬</span>
            <h3 className="text-lg font-semibold text-slate-900">Biyometrik İmza</h3>
          </div>
          <div className="bg-white rounded p-4 font-mono text-sm text-slate-700 break-all border-2 border-dashed border-teal-200">
            {biometricCode}
          </div>
          <p className="text-xs text-slate-600 mt-3">
            Bu biyometrik kod, kaplumbağanın kabuk desenini tamamen temsil eder ve tanımlamada kullanılır.
          </p>
        </div>
      )}

      {/* Similarity Score */}
      {similarityScore !== undefined && (
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border border-green-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <h3 className="text-lg font-semibold text-slate-900">Benzerlik Skoru</h3>
            </div>
            <div
              className={cn(
                'px-4 py-2 rounded-full font-bold text-lg',
                similarityScore >= 0.9
                  ? 'bg-green-500 text-white'
                  : similarityScore >= 0.7
                    ? 'bg-yellow-500 text-white'
                    : 'bg-orange-500 text-white'
              )}
            >
              {(similarityScore * 100).toFixed(1)}%
            </div>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={cn(
                'h-full transition-all duration-500 ease-out',
                similarityScore >= 0.9
                  ? 'bg-gradient-to-r from-green-400 to-green-600'
                  : similarityScore >= 0.7
                    ? 'bg-gradient-to-r from-yellow-400 to-yellow-600'
                    : 'bg-gradient-to-r from-orange-400 to-orange-600'
              )}
              style={{ width: `${similarityScore * 100}%` }}
            />
          </div>

          <p className="text-sm text-slate-700 mt-4">
            {similarityScore >= 0.9
              ? '✓ Bu bireyin daha önce görüldüğü tespit edilmiştir.'
              : similarityScore >= 0.7
                ? '⚠ Potansiyel eşleşme bulundu, manuel doğrulama önerilir.'
                : '● Yeni bir bireydir, veritabanında kayıtlı değildir.'}
          </p>
        </div>
      )}

      {/* Processing Info */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <p className="text-sm text-slate-600 mb-1">Durum</p>
          <p className="text-lg font-semibold">
            {isProcessing ? (
              <span className="flex items-center gap-2 text-blue-600">
                <Loader2 className="w-4 h-4 animate-spin" />
                İşleniyor...
              </span>
            ) : completedStepsCount === steps.length ? (
              <span className="flex items-center gap-2 text-green-600">
                <CheckCircle2 className="w-4 h-4" />
                Tamamlandı
              </span>
            ) : steps.some((s) => s.status === 'error') ? (
              <span className="flex items-center gap-2 text-red-600">
                <AlertCircle className="w-4 h-4" />
                Hata
              </span>
            ) : (
              'Beklemede'
            )}
          </p>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <p className="text-sm text-slate-600 mb-1">Geçen Süre</p>
          <p className="text-lg font-semibold">{displayTime.toFixed(1)}s</p>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-900">
          <strong>ℹ️ Zararsız Tanımlama (Non-Invasive):</strong> Bu sistem, geleneksel
          markalamadan farklı olarak kaplumbağaya hiçbir zarar vermez. Yalnızca fotoğraf
          tabanlı biyometrik tanımlama kullanır.
        </p>
      </div>
    </div>
  )
}

export default ProcessingState
