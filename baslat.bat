@echo off
echo ╔══════════════════════════════════════════════════════════╗
echo ║         Turtle-ID MAS - Otomatik Baslatma Araci          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo Lutfen acilan siyah pencereleri Kapatmayin!
echo Uygulamanizi tarayicidan kullanmaya baslayabilirsiniz.
echo.

:: 1. Python Yapay Zeka Sunucusunu yeni pencerede başlat
echo [+] Yapay Zeka Sunucusu (Port 5000) baslatiliyor...
start "AI Backend (Python)" cmd /k "cd image-analysis-agent && .\venv\Scripts\activate && python app.py"

:: 2. 3 saniye bekle
timeout /t 3 /nobreak > nul

:: 3. Frontend Arayüz Sunucusunu yeni pencerede başlat
echo [+] Web Arayuzu (Frontend) baslatiliyor...
start "Frontend (Vite)" cmd /k "cd frontend && npm run dev"

echo.
echo Baslatma tamamlandi! 
echo Eger tarayici otomatik acilmazsa, http://localhost:5173 adresine gidebilirsiniz.
echo Cikmak isterseniz acilan iki siyah pencereyi (cmd) kapatmaniz yeterlidir.
pause
