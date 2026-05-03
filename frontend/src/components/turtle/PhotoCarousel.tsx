import React, { useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface Photo {
  id: string
  imageUrl?: string
  location: string
  dateSighted: string
}

interface PhotoCarouselProps {
  photos: Photo[]
}

const PhotoCarousel: React.FC<PhotoCarouselProps> = ({ photos }) => {
  const [currentIndex, setCurrentIndex] = useState(0)

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : photos.length - 1))
  }

  const handleNext = () => {
    setCurrentIndex((prev) => (prev < photos.length - 1 ? prev + 1 : 0))
  }

  if (photos.length === 0) {
    return (
      <div className="bg-slate-100 rounded-lg p-12 text-center">
        <span className="text-4xl mb-4 block">📸</span>
        <p className="text-slate-500">Fotoğraf bulunmadı</p>
      </div>
    )
  }

  const currentPhoto = photos[currentIndex]

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <div className="space-y-3">
      {/* Main Image */}
      <div className="relative bg-slate-100 rounded-lg overflow-hidden aspect-video">
        {currentPhoto.imageUrl ? (
          <img
            src={currentPhoto.imageUrl}
            alt={`Fotoğraf - ${currentPhoto.location}`}
            className="w-full h-full object-cover"
            onError={(e) => {
              const target = e.target as HTMLImageElement
              target.src =
                'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" fill="%23cbd5e1" viewBox="0 0 24 24"%3E%3Cpath d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/%3E%3C/svg%3E'
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-slate-200">
            <span className="text-5xl">🖼️</span>
          </div>
        )}

        {/* Navigation Buttons */}
        {photos.length > 1 && (
          <>
            <button
              onClick={handlePrevious}
              className="absolute left-3 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/40 hover:bg-black/60 text-white transition-colors"
              aria-label="Önceki"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              onClick={handleNext}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/40 hover:bg-black/60 text-white transition-colors"
              aria-label="Sonraki"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </>
        )}

        {/* Counter */}
        <div className="absolute top-3 right-3 bg-black/60 text-white px-3 py-1 rounded-full text-sm font-medium">
          {currentIndex + 1} / {photos.length}
        </div>
      </div>

      {/* Photo Info */}
      <div className="bg-white rounded-lg border border-slate-200 p-3">
        <p className="text-sm font-semibold text-slate-900">{currentPhoto.location}</p>
        <p className="text-xs text-slate-600 mt-1">{formatDate(currentPhoto.dateSighted)}</p>
      </div>

      {/* Thumbnail Strip */}
      {photos.length > 1 && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {photos.map((photo, idx) => (
            <button
              key={photo.id}
              onClick={() => setCurrentIndex(idx)}
              className={`flex-shrink-0 w-16 h-16 rounded-lg border-2 transition-all overflow-hidden ${idx === currentIndex
                  ? 'border-teal-500 ring-2 ring-teal-300'
                  : 'border-slate-200 hover:border-slate-300'
                }`}
            >
              {photo.imageUrl ? (
                <img
                  src={photo.imageUrl}
                  alt={`Thumbnail ${idx + 1}`}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full bg-slate-200 flex items-center justify-center text-xs">
                  📸
                </div>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default PhotoCarousel
