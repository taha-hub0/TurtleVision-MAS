import React, { useEffect } from 'react'
import { X, ChevronLeft, ChevronRight } from 'lucide-react'

interface GalleryModalProps {
  isOpen: boolean
  photos: Array<{
    id: string
    imageUrl?: string
    location: string
    dateSighted: string
    observerName: string
    notes?: string
  }>
  currentIndex: number
  onClose: () => void
  onPrevious: () => void
  onNext: () => void
}

const GalleryModal: React.FC<GalleryModalProps> = ({
  isOpen,
  photos,
  currentIndex,
  onClose,
  onPrevious,
  onNext,
}) => {
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') onPrevious()
      if (e.key === 'ArrowRight') onNext()
      if (e.key === 'Escape') onClose()
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onPrevious, onNext, onClose])

  if (!isOpen || photos.length === 0) return null

  const currentPhoto = photos[currentIndex]

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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      {/* Main Modal Container */}
      <div className="w-full h-full flex flex-col items-center justify-center px-4">
        {/* Header */}
        <div className="absolute top-0 left-0 right-0 flex items-center justify-between p-4 text-white">
          <span className="text-sm font-medium">
            {currentIndex + 1} / {photos.length}
          </span>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            aria-label="Kapat"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Image Container */}
        <div className="relative flex items-center justify-center w-full max-w-5xl max-h-[70vh]">
          {currentPhoto.imageUrl ? (
            <img
              src={currentPhoto.imageUrl}
              alt={`Fotoğraf ${currentIndex + 1}`}
              className="max-h-full max-w-full object-contain rounded-lg"
            />
          ) : (
            <div className="w-full h-96 bg-slate-700 rounded-lg flex items-center justify-center text-white">
              Resim bulunamadı
            </div>
          )}

          {/* Previous Button */}
          {currentIndex > 0 && (
            <button
              onClick={onPrevious}
              className="absolute left-4 p-3 rounded-full bg-white/20 hover:bg-white/30 text-white transition-all hover:scale-110"
              aria-label="Önceki"
            >
              <ChevronLeft className="w-6 h-6" />
            </button>
          )}

          {/* Next Button */}
          {currentIndex < photos.length - 1 && (
            <button
              onClick={onNext}
              className="absolute right-4 p-3 rounded-full bg-white/20 hover:bg-white/30 text-white transition-all hover:scale-110"
              aria-label="Sonraki"
            >
              <ChevronRight className="w-6 h-6" />
            </button>
          )}
        </div>

        {/* Metadata Footer */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent px-4 py-6 text-white rounded-b-lg">
          <div className="max-w-5xl mx-auto space-y-2">
            <p className="text-lg font-semibold">{currentPhoto.location}</p>
            <p className="text-sm text-gray-300">{formatDate(currentPhoto.dateSighted)}</p>
            <p className="text-sm text-gray-300">Gözlemci: {currentPhoto.observerName}</p>
            {currentPhoto.notes && (
              <p className="text-sm text-gray-200 italic mt-2">"{currentPhoto.notes}"</p>
            )}
          </div>
        </div>
      </div>

      {/* Keyboard Info (Mobile) */}
      <div className="absolute top-20 left-4 text-white/60 text-xs hidden sm:block">
        <p>← → tuşları ile gezin</p>
        <p>ESC ile kapat</p>
      </div>
    </div>
  )
}

export default GalleryModal
