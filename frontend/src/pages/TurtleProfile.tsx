import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Loader } from 'lucide-react'
import MainLayout from '../layouts/MainLayout'
import BiometricDisplay from '../components/turtle/BiometricDisplay'
import SightingHistory from '../components/turtle/SightingHistory'
import TurtleStats from '../components/turtle/TurtleStats'
import RelatedTurtles from '../components/turtle/RelatedTurtles'
import PhotoGallery from '../components/turtle/PhotoGallery'
import GalleryModal from '../components/turtle/GalleryModal'
import { getTurtleById, getRelatedTurtles } from '../api/services/turtleService'
import type { Turtle } from '../types/turtle'

const TurtleProfile: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [turtle, setTurtle] = useState<Turtle | null>(null)
  const [related, setRelated] = useState<Array<{ turtle: Turtle; similarity: number }>>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [galleryOpen, setGalleryOpen] = useState(false)
  const [selectedPhotoIndex, setSelectedPhotoIndex] = useState(0)

  useEffect(() => {
    if (!id) {
      setError('Kaplumbağa ID\'si belirtilmedi')
      setLoading(false)
      return
    }

    const loadTurtle = async () => {
      try {
        setLoading(true)
        setError(null)

        const data = await getTurtleById(id)
        if (!data) {
          setError(`ID '${id}' ile kaplumbağa bulunamadı`)
          setTurtle(null)
          setRelated([])
          return
        }

        setTurtle(data)

        // Load related turtles
        const relatedData = await getRelatedTurtles(data.biometric_code)
        setRelated(relatedData)
      } catch (err) {
        setError(`Bir hata oluştu: ${err instanceof Error ? err.message : 'Bilinmeyen hata'}`)
      } finally {
        setLoading(false)
      }
    }

    loadTurtle()
  }, [id])

  const handleRelatedSelect = (relatedId: string) => {
    navigate(`/turtle/${relatedId}`)
  }

  const handlePhotoClick = (index: number) => {
    setSelectedPhotoIndex(index)
    setGalleryOpen(true)
  }

  const handlePreviousPhoto = () => {
    setSelectedPhotoIndex((prev) => (prev > 0 ? prev - 1 : (turtle?.sightings?.length || 1) - 1))
  }

  const handleNextPhoto = () => {
    setSelectedPhotoIndex((prev) => (prev < (turtle?.sightings?.length || 1) - 1 ? prev + 1 : 0))
  }

  if (loading) {
    return (
      <MainLayout>
        <div className="flex flex-col items-center justify-center py-16">
          <Loader className="w-8 h-8 text-teal-500 animate-spin mb-4" />
          <p className="text-slate-600">Kaplumbağa profili yükleniyor...</p>
        </div>
      </MainLayout>
    )
  }

  if (error || !turtle) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-teal-600 hover:text-teal-700 font-medium transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Dashboard'a Dön
          </button>

          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-red-700 mb-2">Hata</h2>
            <p className="text-red-600">{error || 'Kaplumbağa bulunamadı'}</p>
          </div>
        </div>
      </MainLayout>
    )
  }

  const speciesLabels: Record<string, string> = {
    GREEN_TURTLE: 'Yeşil Kaplumbağa',
    LOGGERHEAD: 'Sarı Başlı Kaplumbağa',
    LEATHERBACK: 'Deri Kaplumbağa',
    HAWKSBILL: 'Şahin Kaplumbağa',
  }

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-teal-600 hover:text-teal-700 font-medium transition-colors mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            Geri Dön
          </button>

          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-4 flex-1">
              <div className="w-16 h-16 bg-gradient-to-br from-teal-400 to-blue-600 rounded-lg flex items-center justify-center text-4xl">
                🐢
              </div>
              <div>
                <h1 className="text-4xl font-bold text-slate-900">
                  {speciesLabels[turtle.species] || turtle.species}
                </h1>
                <p className="text-slate-600 mt-1">ID: {turtle.id}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Biometric Code */}
        <BiometricDisplay code={turtle.biometric_code} vector={turtle.biometric_vector} />

        {/* Stats and Health */}
        <TurtleStats turtle={turtle} />

        {/* Photo Gallery */}
        {turtle.sightings && turtle.sightings.length > 0 && (
          <PhotoGallery
            photos={turtle.sightings.map((s) => ({
              id: s.id,
              imageUrl: s.imageUrl,
              location: s.location,
              dateSighted: s.dateSighted,
              observerName: s.observerName,
              notes: s.notes,
            }))}
            onPhotoClick={handlePhotoClick}
          />
        )}

        {/* Sighting History */}
        {turtle.sightings && turtle.sightings.length > 0 && (
          <SightingHistory sightings={turtle.sightings} />
        )}

        {/* Related Turtles */}
        {related.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-900">Benzer Kaplumbağalar</h3>
              <p className="text-xs text-slate-600">Bu kaplumbağaların biometrik kodları bu bireye benziyor</p>
            </div>
            <RelatedTurtles
              turtles={related}
              onSelect={handleRelatedSelect}
            />
          </div>
        )}

        {/* Footer Navigation */}
        <div className="flex gap-4 pt-8 border-t border-slate-200">
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-3 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors font-medium"
          >
            Dashboard'a Dön
          </button>
          <button
            onClick={() => navigate('/identification')}
            className="px-6 py-3 bg-gradient-to-r from-teal-500 to-blue-600 text-white rounded-lg hover:shadow-lg transition-shadow font-medium"
          >
            Yeni Analiz Başlat
          </button>
        </div>
      </div>

      {/* Gallery Modal */}
      {turtle && turtle.sightings && (
        <GalleryModal
          isOpen={galleryOpen}
          photos={turtle.sightings.map((s) => ({
            id: s.id,
            imageUrl: s.imageUrl,
            location: s.location,
            dateSighted: s.dateSighted,
            observerName: s.observerName,
            notes: s.notes,
          }))}
          currentIndex={selectedPhotoIndex}
          onClose={() => setGalleryOpen(false)}
          onPrevious={handlePreviousPhoto}
          onNext={handleNextPhoto}
        />
      )}
    </MainLayout>
  )
}

export default TurtleProfile
