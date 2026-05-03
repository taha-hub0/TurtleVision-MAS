import React from 'react'
import { Play } from 'lucide-react'

interface Photo {
  id: string
  imageUrl?: string
  location: string
  dateSighted: string
  observerName: string
  notes?: string
}

interface PhotoGalleryProps {
  photos: Photo[]
  onPhotoClick: (index: number) => void
}

const PhotoGallery: React.FC<PhotoGalleryProps> = ({ photos, onPhotoClick }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  if (photos.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-slate-200 p-12 text-center">
        <span className="text-4xl mb-4 block">📸</span>
        <p className="text-slate-500">Henüz fotoğraf bulunmadı</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6">
      <h3 className="text-lg font-semibold text-slate-900 mb-6">📸 Fotoğraf Galerisi</h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {photos.map((photo, idx) => (
          <button
            key={photo.id}
            onClick={() => onPhotoClick(idx)}
            className="group relative overflow-hidden rounded-lg border border-slate-200 transition-all hover:border-teal-400 hover:shadow-lg"
          >
            {/* Image */}
            <div className="aspect-video bg-slate-100 overflow-hidden">
              {photo.imageUrl ? (
                <img
                  src={photo.imageUrl}
                  alt={`Fotoğraf - ${photo.location}`}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement
                    target.src =
                      'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" fill="%23cbd5e1" viewBox="0 0 24 24"%3E%3Cpath d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/%3E%3C/svg%3E'
                  }}
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-slate-200">
                  <span className="text-4xl">🖼️</span>
                </div>
              )}
            </div>

            {/* Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-3">
              <div className="flex items-center gap-2 text-white">
                <Play className="w-4 h-4 fill-white" />
                <span className="text-sm font-medium">Görüntüle</span>
              </div>
            </div>

            {/* Counter Badge */}
            <div className="absolute top-2 right-2 w-6 h-6 bg-teal-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
              {idx + 1}
            </div>
          </button>
        ))}
      </div>

      {/* Info Footer */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <p className="text-xs text-slate-600 text-center">
          {photos.length} fotoğraf • Tıkla ve başka resimler arasında geç
        </p>
      </div>
    </div>
  )
}

export default PhotoGallery
