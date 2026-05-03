import React, { useState, useRef } from 'react'
import { Upload, X, Crop } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import ReactCrop, { type Crop as CropType, centerCrop, makeAspectCrop } from 'react-image-crop'
import 'react-image-crop/dist/ReactCrop.css'
import MainLayout from '../layouts/MainLayout'
import ProcessingState from '../components/processing/ProcessingState'
import type { ProcessingStep } from '../types/turtle'

const Identification: React.FC = () => {
  const navigate = useNavigate()
  const [step, setStep] = useState<1 | 2 | 3>(1)
  const [image, setImage] = useState<string | null>(null) // Raw uploaded image
  const [croppedImage, setCroppedImage] = useState<string | null>(null) // Final image to send
  
  // Cropper states
  const [crop, setCrop] = useState<CropType>()
  const imgRef = useRef<HTMLImageElement>(null)
  const [isCropping, setIsCropping] = useState(false)

  const [location, setLocation] = useState<string>('Bilinmiyor')
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingSteps, setProcessingSteps] = useState<ProcessingStep[]>([
    { id: 'validation', label: 'Doğrulama', status: 'pending' },
    { id: 'analysis', label: 'Analiz', status: 'pending' },
    { id: 'matching', label: 'Eşleştirme', status: 'pending' },
    { id: 'reporting', label: 'Rapor', status: 'pending' },
  ])
  const [result, setResult] = useState({
    biometricCode: '',
    similarityScore: 0,
    analysisTime: 0,
    matchedId: '',
    classification: '',
  })

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        setImage(event.target?.result as string)
        setIsCropping(true) // Open crop mode
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
        setIsCropping(true) // Open crop mode
      }
      reader.readAsDataURL(file)
    }
  }

  const onImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const { width, height } = e.currentTarget
    const initialCrop = centerCrop(
      makeAspectCrop({ unit: '%', width: 50 }, 1, width, height),
      width,
      height
    )
    setCrop(initialCrop)
  }

  const handleCropComplete = () => {
    if (!imgRef.current || !crop || crop.width === 0 || crop.height === 0) {
      setCroppedImage(image) // If no crop, use original
      setIsCropping(false)
      return
    }

    const canvas = document.createElement('canvas')
    const scaleX = imgRef.current.naturalWidth / imgRef.current.width
    const scaleY = imgRef.current.naturalHeight / imgRef.current.height
    
    canvas.width = crop.width * scaleX
    canvas.height = crop.height * scaleY
    
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.drawImage(
      imgRef.current,
      crop.x * scaleX,
      crop.y * scaleY,
      crop.width * scaleX,
      crop.height * scaleY,
      0,
      0,
      crop.width * scaleX,
      crop.height * scaleY
    )

    const base64Cropped = canvas.toDataURL('image/jpeg', 1.0)
    setCroppedImage(base64Cropped)
    setIsCropping(false)
  }

  const handleFormSubmit = async () => {
    setStep(2)
    setIsProcessing(true)
    const startTime = performance.now()

    const initialSteps: ProcessingStep[] = [
      { id: 'validation', label: 'Doğrulama', status: 'processing', duration: 0.5 },
      { id: 'analysis', label: 'Görüntü Analizi (ResNet50)', status: 'pending' },
      { id: 'matching', label: 'Kaggle Veritabanı Eşleştirme', status: 'pending' },
      { id: 'reporting', label: 'Rapor', status: 'pending' },
    ]
    setProcessingSteps(initialSteps)

    try {
      // Use croppedImage instead of raw image
      const base64Data = croppedImage?.split(',')[1] || image?.split(',')[1] || ''

      // Adım 1: Doğrulama tamamlandı, Analiz başlıyor
      setProcessingSteps(prev => prev.map((s, i) => i === 0 ? { ...s, status: 'success' } : i === 1 ? { ...s, status: 'processing' } : s))

      // 1. Python Backend'den Analiz İsteği (Özellik Çıkarımı)
      const analyzeRes = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: base64Data, metadata: {} })
      })
      const analyzeData = await analyzeRes.json()
      
      if (!analyzeData.success) throw new Error('Analiz başarısız')
      const features = analyzeData.features

      // Adım 2: Analiz tamamlandı, Eşleştirme başlıyor
      setProcessingSteps(prev => prev.map((s, i) => i === 1 ? { ...s, status: 'success' } : i === 2 ? { ...s, status: 'processing' } : s))

      // 2. Python Backend'den Eşleştirme İsteği (Kaggle veritabanı kıyaslaması)
      const matchRes = await fetch('http://localhost:5000/api/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ biometric_vector: features })
      })
      const matchData = await matchRes.json()
      if (!matchData.success) throw new Error('Eşleştirme başarısız')

      const endTime = performance.now()

      // Sonuçları state'e kaydet
      setResult({
        biometricCode: 'RSNT50-128D-' + features.slice(0,3).map((f: number) => Math.abs(f).toFixed(2).replace('.','')).join(''),
        similarityScore: matchData.similarity_score, // Gerçek skor
        analysisTime: Number(((endTime - startTime) / 1000).toFixed(2)),
        matchedId: matchData.matched_turtle_id || 'Yeni Birey',
        classification: matchData.classification
      })
      
      // Kaydetme fonksiyonu için özellikleri kaydet
      ;(window as any).__lastFeatures = features;

      // Adım 3: Eşleştirme tamamlandı, Rapor hazırlanıyor
      setProcessingSteps(prev => prev.map((s, i) => i === 2 ? { ...s, status: 'success' } : i === 3 ? { ...s, status: 'processing' } : s))
      
      setTimeout(() => {
        setProcessingSteps(prev => prev.map(s => s.id === 'reporting' ? { ...s, status: 'success' } : s))
        setIsProcessing(false)
        setStep(3)
      }, 500)

    } catch (error) {
      console.error('API Hatası:', error)
      alert('Arka plan servisi (Python 5000 portu) çalışmıyor veya hata oluştu.')
      setIsProcessing(false)
      setStep(1)
    }
  }

  const handleRegisterToDB = async () => {
    const features = (window as any).__lastFeatures;
    if (!features) return;
    
    // Use croppedImage instead of raw image
    const base64Data = croppedImage?.split(',')[1] || image?.split(',')[1] || '';
    
    try {
      const res = await fetch('http://localhost:5000/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          biometric_vector: features,
          image: base64Data,
          location: location
        })
      })
      const data = await res.json()
      if (data.success) {
        alert('Fotoğraf başarıyla veritabanına eklendi! (ID: ' + data.turtle_id + ')\nŞimdi aynı fotoğrafı tekrar analiz ettiğinizde %100 eşleşme bulacaktır.')
      } else {
        alert('Kaydetme hatası: ' + data.error)
      }
    } catch (e) {
      alert('Sunucuya bağlanılamadı.')
    }
  }

  return (
    <MainLayout>
      <div className="space-y-8">
        <div>
          <h1 className="text-4xl font-bold text-slate-900">Yeni Analiz</h1>
          <p className="text-slate-600 mt-1">Deniz kaplumbağasını fotoğrafından tanımlayın</p>
          <button 
            onClick={() => navigate('/gallery')}
            className="mt-4 px-4 py-2 bg-indigo-50 text-indigo-600 border border-indigo-200 rounded-lg hover:bg-indigo-100 transition-colors font-medium text-sm flex items-center gap-2"
          >
            <span>📷</span> Sisteme Kayıtlı Görselleri Gör (Galeri)
          </button>
        </div>

        {/* Step 1: Image Upload */}
        {step === 1 && (
          <div className="bg-white rounded-lg border border-slate-200 p-8">
            <h2 className="text-xl font-semibold mb-6">Görüntü Yükle</h2>
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
              ) : isCropping ? (
                <div className="space-y-4">
                  <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 inline-block max-w-full overflow-hidden">
                    <p className="text-sm font-medium text-slate-700 mb-3 flex items-center justify-center gap-2">
                      <Crop className="w-4 h-4" /> Lütfen kaplumbağanın yüzünü veya kabuğunu seçin
                    </p>
                    <ReactCrop 
                      crop={crop} 
                      onChange={c => setCrop(c)} 
                      aspect={1} 
                      className="max-h-[50vh] mx-auto"
                    >
                      <img 
                        ref={imgRef} 
                        src={image} 
                        onLoad={onImageLoad} 
                        alt="Crop Preview" 
                        className="max-h-[50vh] w-auto mx-auto" 
                        style={{ maxWidth: '100%' }}
                      />
                    </ReactCrop>
                  </div>
                  <div className="flex justify-center gap-4 mt-6">
                    <button
                      onClick={() => { setImage(null); setIsCropping(false); setCroppedImage(null); }}
                      className="text-slate-500 hover:text-slate-700 px-4 py-2 flex items-center gap-2 border border-slate-200 rounded-lg transition-colors"
                    >
                      <X className="w-4 h-4" /> İptal Et
                    </button>
                    <button
                      onClick={handleCropComplete}
                      className="px-6 py-2 bg-gradient-to-r from-teal-500 to-blue-600 text-white font-bold rounded-lg hover:shadow-lg transition-all"
                    >
                      Kırp ve Onayla
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="relative inline-block">
                    <img src={croppedImage || image} alt="Final Cropped" className="max-h-64 mx-auto rounded-lg shadow-sm border border-slate-200" />
                    <button 
                      onClick={() => setIsCropping(true)}
                      className="absolute top-2 right-2 bg-white/90 text-slate-700 p-2 rounded-full shadow hover:bg-teal-50 hover:text-teal-600 transition-colors"
                      title="Yeniden Kırp"
                    >
                      <Crop className="w-4 h-4" />
                    </button>
                  </div>
                  
                  <div className="mt-6 max-w-sm mx-auto text-left bg-teal-50/50 p-4 rounded-lg border border-teal-100">
                    <label className="block text-sm font-semibold text-slate-800 mb-2">📍 Bu kaplumbağayı nerede gördünüz?</label>
                    <select 
                      value={location} 
                      onChange={(e) => setLocation(e.target.value)}
                      className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-teal-500 outline-none text-slate-700 font-medium"
                    >
                      <option value="Bilinmiyor">Bilinmiyor (Laboratuvar / Arşiv)</option>
                      <option value="İztuzu Plajı, Dalyan">İztuzu Plajı, Dalyan</option>
                      <option value="Kaş, Antalya">Kaş, Antalya</option>
                      <option value="Patara Plajı, Antalya">Patara Plajı, Antalya</option>
                      <option value="Ölüdeniz, Fethiye">Ölüdeniz, Fethiye</option>
                      <option value="Samandağ, Hatay">Samandağ, Hatay</option>
                    </select>
                  </div>

                  <div className="flex justify-center gap-4 mt-8">
                    <button
                      onClick={() => { setImage(null); setCroppedImage(null); }}
                      className="text-slate-500 hover:text-slate-700 px-4 py-2 flex items-center gap-2 border border-slate-200 rounded-lg transition-colors"
                    >
                      <X className="w-4 h-4" /> Temizle
                    </button>
                    <button
                      onClick={handleFormSubmit}
                      className="px-8 py-2.5 bg-gradient-to-r from-teal-500 to-blue-600 text-white font-bold rounded-lg hover:shadow-lg transition-all transform hover:-translate-y-0.5"
                    >
                      Hemen Analiz Et →
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 2 & 3: Processing & Results */}
        {step >= 2 && (
          <div className="relative">
            {step === 2 && (
              <div className="absolute -top-12 right-0">
                <button
                  onClick={() => {
                    setIsProcessing(false)
                    setStep(1)
                  }}
                  className="text-red-500 hover:text-red-700 flex items-center gap-2 text-sm font-medium"
                >
                  <X className="w-4 h-4" /> İptal Et
                </button>
              </div>
            )}
            
            <ProcessingState
              steps={processingSteps}
              isProcessing={isProcessing}
              biometricCode={result.biometricCode}
              similarityScore={result.similarityScore}
              elapsedTime={result.analysisTime}
            />
            
            {step === 3 && (
              <div className="mt-8 flex justify-center gap-4">
                <button
                  onClick={handleRegisterToDB}
                  className="px-6 py-2 bg-slate-800 text-white font-medium rounded-lg hover:bg-slate-900 transition-colors shadow-sm"
                >
                  Bu Kaplumbağayı Veritabanına Kaydet
                </button>
                <button
                  onClick={() => {
                    setImage(null)
                    setCroppedImage(null)
                    setStep(1)
                  }}
                  className="px-6 py-2 border-2 border-teal-500 text-teal-600 font-medium rounded-lg hover:bg-teal-50 transition-colors"
                >
                  Yeni Görüntü Yükle
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </MainLayout>
  )
}

export default Identification
