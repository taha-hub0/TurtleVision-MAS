import React, { useState, useEffect } from 'react'
import { Trash2 } from 'lucide-react'
import MainLayout from '../layouts/MainLayout'

const Gallery: React.FC = () => {
  const [galleryImages, setGalleryImages] = useState<{id: string, url: string, location?: string}[]>([])

  useEffect(() => {
    loadGallery()
  }, [])

  const loadGallery = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/gallery')
      const data = await res.json()
      if (data.success) {
        setGalleryImages(data.images)
      }
    } catch (e) {
      console.error('Galeri yüklenemedi.')
    }
  }

  const handleDeleteImage = async (id: string) => {
    if (!window.confirm('Bu görseli ve sistemdeki tüm eşleşme kayıtlarını silmek istediğinize emin misiniz?')) return;
    
    try {
      const res = await fetch(`http://localhost:5000/api/gallery/${id}`, {
        method: 'DELETE'
      });
      const data = await res.json();
      if (data.success) {
        setGalleryImages(prev => prev.filter(img => img.id !== id));
      } else {
        alert('Silinemedi: ' + data.error);
      }
    } catch (e) {
      alert('Sunucu hatası. Silme başarısız.');
    }
  }

  return (
    <MainLayout>
      <div className="space-y-8">
        <div>
          <h1 className="text-4xl font-bold text-slate-900">Sistem Galerisi</h1>
          <p className="text-slate-600 mt-1">Veritabanına kayıtlı tüm bireylerin fiziksel görselleri ve kayıtları</p>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-8 shadow-sm">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-slate-800">Kayıtlı Kaplumbağalar</h2>
            <span className="px-3 py-1 bg-teal-50 text-teal-700 rounded-full text-sm font-semibold border border-teal-100">
              Toplam: {galleryImages.length}
            </span>
          </div>

          {galleryImages.length === 0 ? (
            <div className="text-center py-12 bg-slate-50 rounded-lg border-2 border-dashed border-slate-200">
              <p className="text-slate-500 font-medium">Henüz veritabanına kaydedilmiş görsel bulunmuyor.</p>
              <p className="text-slate-400 text-sm mt-1">Yeni Analiz sayfasından tarama yaparak kayıt ekleyebilirsiniz.</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {galleryImages.map((img, i) => (
                <div key={i} className="border border-slate-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow relative group bg-white flex flex-col">
                  <div className="aspect-square w-full relative">
                    <img src={img.url} alt={img.id} className="w-full h-full object-cover" />
                  </div>
                  <div className="p-3 bg-slate-50 border-t border-slate-100 flex-1 flex flex-col">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-mono text-sm font-bold text-slate-800 truncate" title={img.id}>
                        {img.id}
                      </span>
                      <button 
                        onClick={() => handleDeleteImage(img.id)}
                        className="text-slate-400 hover:text-red-500 transition-colors p-1 hover:bg-red-50 rounded-md -mt-1 -mr-1"
                        title="Sistemden Tamamen Sil"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium mt-auto">
                      <span className="text-teal-600">📍</span>
                      <span className="truncate" title={img.location || 'Bilinmiyor'}>{img.location || 'Bilinmiyor'}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  )
}

export default Gallery
