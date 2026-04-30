import React, { useState } from 'react'
import { Upload, X } from 'lucide-react'
import MainLayout from '../layouts/MainLayout'
import ProcessingState from '../components/processing/ProcessingState.tsx'
import FormInput from '../components/common/FormInput'
import FormSelect from '../components/common/FormSelect'
import { TURTLE_SPECIES, WEATHER_OPTIONS, WATER_CLARITY_OPTIONS } from '../utils/constants'
import type { ProcessingStep } from '../types/turtle'

const Identification: React.FC = () => {
  const [step, setStep] = useState<1 | 2 | 3 | 4 | 5>(1)
  const [image, setImage] = useState<string | null>(null)
  const [species, setSpecies] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingSteps, setProcessingSteps] = useState<ProcessingStep[]>([
    { id: 'validation', label: 'Doğrulama', status: 'pending' },
    { id: 'analysis', label: 'Analiz', status: 'pending' },
    { id: 'matching', label: 'Eşleştirme', status: 'pending' },
    { id: 'reporting', label: 'Rapor', status: 'pending' },
  ])
  const [formData, setFormData] = useState({
    latitude: '',
    longitude: '',
    accuracy: '',
    observerName: '',
    observerEmail: '',
    waterTemperature: '',
    weather: '',
    waterClarity: '',
  })
  const [result] = useState({
    biometricCode: '101101011101110110',
    similarityScore: 0.92,
    analysisTime: 2.3,
  })

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        setImage(event.target?.result as string)
        setStep(2)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleDragDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        setImage(event.target?.result as string)
        setStep(2)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleFormSubmit = async () => {
    setStep(4)
    setIsProcessing(true)

    const steps_data: ProcessingStep[] = [
      { id: 'validation', label: 'Doğrulama', status: 'processing', duration: 0.5 },
      { id: 'analysis', label: 'Analiz', status: 'pending' },
      { id: 'matching', label: 'Eşleştirme', status: 'pending' },
      { id: 'reporting', label: 'Rapor', status: 'pending' },
    ]
    setProcessingSteps(steps_data)

    setTimeout(() => {
      setProcessingSteps((prev) =>
        prev.map((s, i) =>
          i === 0 ? { ...s, status: 'success' } : i === 1 ? { ...s, status: 'processing', duration: 2.3 } : s
        )
      )
    }, 2000)

    setTimeout(() => {
      setProcessingSteps((prev) =>
        prev.map((s, i) =>
          i === 1 ? { ...s, status: 'success' } : i === 2 ? { ...s, status: 'processing', duration: 1.1 } : s
        )
      )
    }, 4500)

    setTimeout(() => {
      setProcessingSteps((prev) =>
        prev.map((s, i) =>
          i === 2 ? { ...s, status: 'success' } : i === 3 ? { ...s, status: 'processing', duration: 0.8 } : s
        )
      )
    }, 5800)

    setTimeout(() => {
      setProcessingSteps((prev) => prev.map((s, i) => (i === 3 ? { ...s, status: 'success' } : s)))
      setIsProcessing(false)
      setStep(5)
    }, 6800)
  }

  return (
    <MainLayout>
      <div className="space-y-8">
        <div>
          <h1 className="text-4xl font-bold text-slate-900">Yeni Analiz</h1>
          <p className="text-slate-600 mt-1">Deniz kaplumbağasını fotoğrafından tanımlayın</p>
        </div>

        {/* Step 1: Image Upload */}
        {step >= 1 && (
          <div className="bg-white rounded-lg border border-slate-200 p-8">
            <h2 className="text-xl font-semibold mb-6">Adım 1: Görüntü Yükle</h2>
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDragDrop}
              className="border-2 border-dashed border-slate-300 rounded-lg p-12 text-center hover:border-teal-500 transition-colors"
            >
              {!image ? (
                <div className="space-y-4">
                  <Upload className="w-12 h-12 mx-auto text-slate-400" />
                  <div>
                    <p className="text-lg font-medium text-slate-900">Görüntüyü sürükle ve bırak</p>
                    <p className="text-slate-600 text-sm">veya</p>
                  </div>
                  <label className="inline-block bg-teal-500 text-white px-6 py-2 rounded-lg cursor-pointer hover:bg-teal-600 transition-colors">
                    Dosya Seç
                    <input type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
                  </label>
                </div>
              ) : (
                <div className="space-y-4">
                  <img src={image} alt="Uploaded" className="max-h-64 mx-auto rounded-lg" />
                  <button
                    onClick={() => {
                      setImage(null)
                      setStep(1)
                    }}
                    className="text-red-500 hover:text-red-700 flex items-center gap-2 mx-auto transition-colors"
                  >
                    <X className="w-4 h-4" /> Değiştir
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 2: Species Selection */}
        {step >= 2 && (
          <div className="bg-white rounded-lg border border-slate-200 p-8">
            <h2 className="text-xl font-semibold mb-6">Adım 2: Tür Seç</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {TURTLE_SPECIES.map((sp) => (
                <label key={sp.value} className="cursor-pointer">
                  <input
                    type="radio"
                    name="species"
                    value={sp.value}
                    checked={species === sp.value}
                    onChange={(e) => setSpecies(e.target.value)}
                    className="hidden"
                  />
                  <div
                    className={`p-4 rounded-lg border-2 transition-all ${
                      species === sp.value ? 'border-teal-500 bg-teal-50' : 'border-slate-200 hover:border-teal-300'
                    }`}
                  >
                    <p className="font-medium text-slate-900">{sp.label}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Step 3: Metadata Form */}
        {step >= 3 && (
          <div className="bg-white rounded-lg border border-slate-200 p-8">
            <h2 className="text-xl font-semibold mb-6">Adım 3: Meta Veri</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormInput
                type="number"
                placeholder="Enlem (-90 ile 90)"
                label="Enlem"
                value={formData.latitude}
                onChange={(e) => setFormData({ ...formData, latitude: e.target.value })}
              />
              <FormInput
                type="number"
                placeholder="Boylam (-180 ile 180)"
                label="Boylam"
                value={formData.longitude}
                onChange={(e) => setFormData({ ...formData, longitude: e.target.value })}
              />
              <FormInput
                type="text"
                placeholder="Gözlemci Adı"
                label="Gözlemci Adı"
                value={formData.observerName}
                onChange={(e) => setFormData({ ...formData, observerName: e.target.value })}
              />
              <FormInput
                type="email"
                placeholder="Gözlemci E-posta"
                label="Gözlemci E-posta"
                value={formData.observerEmail}
                onChange={(e) => setFormData({ ...formData, observerEmail: e.target.value })}
              />
              <FormInput
                type="number"
                placeholder="Su Sıcaklığı (°C)"
                label="Su Sıcaklığı"
                value={formData.waterTemperature}
                onChange={(e) => setFormData({ ...formData, waterTemperature: e.target.value })}
              />
              <FormSelect
                label="Hava Durumu"
                value={formData.weather}
                onChange={(e) => setFormData({ ...formData, weather: e.target.value })}
              >
                <option>Hava Durumu Seç</option>
                {WEATHER_OPTIONS.map((w) => (
                  <option key={w} value={w}>
                    {w}
                  </option>
                ))}
              </FormSelect>
              <FormSelect
                label="Su Saydamlığı"
                value={formData.waterClarity}
                onChange={(e) => setFormData({ ...formData, waterClarity: e.target.value })}
              >
                <option>Su Saydamlığı Seç</option>
                {WATER_CLARITY_OPTIONS.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </FormSelect>
            </div>
          </div>
        )}

        {/* Step 4: Processing */}
        {step >= 4 && (
          <ProcessingState
            steps={processingSteps}
            isProcessing={isProcessing}
            biometricCode={result.biometricCode}
            similarityScore={result.similarityScore}
            elapsedTime={result.analysisTime}
          />
        )}

        {/* Navigation Buttons */}
        <div className="flex gap-4 justify-end">
          {step > 1 && (
            <button
              onClick={() => setStep((s) => (s - 1) as any)}
              className="px-6 py-2 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
            >
              ← Geri
            </button>
          )}
          {step < 4 && (
            <button
              onClick={() => {
                if (step === 1 && !image) return
                if (step === 2 && !species) return
                if (step === 3) return handleFormSubmit()
                setStep((s) => (s + 1) as any)
              }}
              disabled={!image || (step === 2 && !species)}
              className="px-6 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 disabled:opacity-50 transition-colors"
            >
              İleri →
            </button>
          )}
          {step === 3 && (
            <button
              onClick={handleFormSubmit}
              className="px-6 py-2 bg-gradient-to-r from-teal-500 to-blue-600 text-white rounded-lg hover:shadow-lg transition-shadow"
            >
              Analizi Başlat
            </button>
          )}
        </div>
      </div>
    </MainLayout>
  )
}

export default Identification

