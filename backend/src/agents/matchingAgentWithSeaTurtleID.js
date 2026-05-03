/**
 * Matching Agent - SeaTurtleID2022 Integration
 * =============================================
 * 
 * Backend Eşleştirme Ajanı, Python image-analysis-agent'ıyla birlikte
 * gelen biyometrik vektörü veritabanı kayıtlarıyla karşılaştırır.
 * 
 * İş Akışı:
 * 1. Frontend'den fotoğraf ve biyometrik vektör al
 * 2. Image Analysis Agent'a fotoğrafı gönder (tensor extraction)
 * 3. Python Matching Logic'ten benzerlik hesabını al
 * 4. Sonuca göre "EXISTING_RECORD" veya "NEW_INDIVIDUAL" döndür
 * 5. Reporter Agent'a raporlama için gönder
 * 
 * Non-Invasive Metodoloji:
 * Hayvansal refahı koruyarak biyometrik takip yapıyoruz.
 */

const axios = require('axios');

/**
 * Matching Agent Configuration
 */
const MATCHING_CONFIG = {
    // Python image-analysis-agent endpoint
    imageAnalysisAgent: process.env.IMAGE_ANALYSIS_URL || 'http://localhost:5001',

    // Benzerlik eşik değeri
    similarityThreshold: 0.60, // %60 - SeaTurtleID2022 kriteri

    // Matching method
    matchingMethod: 'cosine', // 'cosine' veya 'euclidean'
};

/**
 * SeaTurtleID Matching Logic (Python Agent ile iletişim)
 */
class SeaTurtleIDMatcher {
    /**
     * Gelen biyometrik vektörü veritabanıyla eşleştir.
     * 
     * @param {Array<number>} biometricVector - 128-boyutlu biyometrik vektör
     * @param {Object} photoMetadata - Fotoğraf metadatası
     * @returns {Promise<Object>} Eşleştirme sonucu
     */
    static async matchTurtle(biometricVector, photoMetadata = {}) {
        try {
            // Python Backend'e eşleştirme isteği gönder
            const response = await axios.post(
                `${MATCHING_CONFIG.imageAnalysisAgent}/api/match`,
                {
                    biometric_vector: biometricVector,
                    threshold: MATCHING_CONFIG.similarityThreshold,
                    method: MATCHING_CONFIG.matchingMethod,
                    metadata: photoMetadata,
                },
                { timeout: 5000 }
            );

            const matchResult = response.data;

            // Sonucu normalize et
            return {
                matched: matchResult.matched,
                classification: matchResult.classification, // EXISTING_RECORD | NEW_INDIVIDUAL
                confidence: matchResult.confidence,
                matchedTurtleId: matchResult.matched_turtle_id,
                similarityScore: matchResult.similarity_score,
                matchingMethod: matchResult.matching_method,
                reasoning: matchResult.reasoning,
                timestamp: new Date().toISOString(),
            };
        } catch (error) {
            console.error('Matching failed:', error.message);
            throw new Error(`Turtle matching error: ${error.message}`);
        }
    }

    /**
     * Top N benzer kayıtla birlikte eşleştirme sonucu döndür.
     * (İnsan müdahalesi gereken durumlar için)
     * 
     * @param {Array<number>} biometricVector - Biyometrik vektör
     * @param {number} topN - Döndürülecek kayıt sayısı
     * @returns {Promise<Object>} Ana sonuç + alternatifler
     */
    static async matchWithAlternatives(biometricVector, topN = 5) {
        try {
            const response = await axios.post(
                `${MATCHING_CONFIG.imageAnalysisAgent}/api/match-top-n`,
                {
                    biometric_vector: biometricVector,
                    top_n: topN,
                    threshold: MATCHING_CONFIG.similarityThreshold,
                    method: MATCHING_CONFIG.matchingMethod,
                },
                { timeout: 5000 }
            );

            return response.data;
        } catch (error) {
            console.error('Top-N matching failed:', error.message);
            throw new Error(`Top-N matching error: ${error.message}`);
        }
    }
}

/**
 * Coordinator'dan çağrılan ana Matching Agent
 * 
 * @param {Object} identificationData - Image Analysis Agent'dan gelen veriler
 *   - photoId: Fotoğraf ID'si
 *   - biometricVector: 128-boyutlu vektör
 *   - location: Konum
 *   - captureDate: Kaydedilme tarihi
 * 
 * @returns {Promise<Object>} Matching sonucu + rapor verisi
 */
async function runMatchingAgent(identificationData) {
    console.log('🔗 Matching Agent başladı');
    console.log('  Foto ID:', identificationData.photoId);
    console.log('  Konum:', identificationData.location);

    try {
        // Python backend'le eşleştirme yap
        const matchResult = await SeaTurtleIDMatcher.matchTurtle(
            identificationData.biometricVector,
            {
                location: identificationData.location,
                capture_date: identificationData.captureDate,
                photo_id: identificationData.photoId,
            }
        );

        console.log('✓ Eşleştirme tamamlandı');
        console.log(`  Sınıflandırma: ${matchResult.classification}`);
        console.log(`  Güven: ${(matchResult.confidence * 100).toFixed(1)}%`);

        // Sonuca göre rapor oluştur
        const reportData = {
            photoId: identificationData.photoId,
            location: identificationData.location,
            captureDate: identificationData.captureDate,
            matchResult: matchResult,

            // Reporter Agent için veri
            reportType: matchResult.classification === 'EXISTING_RECORD'
                ? 'MATCH_FOUND'
                : 'NEW_INDIVIDUAL_FOUND',

            summary: matchResult.reasoning,

            // Korunum açısından önemli bilgiler
            conservationImplications: generateConservationNotes(matchResult),
        };

        return {
            success: true,
            agent: 'MatchingAgent',
            data: reportData,
            nextAgent: 'ReporterAgent', // Sonraki ajan Reporter
        };
    } catch (error) {
        console.error('❌ Matching Agent hatası:', error.message);

        return {
            success: false,
            agent: 'MatchingAgent',
            error: error.message,
            data: {
                photoId: identificationData.photoId,
                fallbackClassification: 'MANUAL_REVIEW_REQUIRED',
                reason: 'Matching logic unavailable, human review needed',
            },
        };
    }
}

/**
 * Koruma açısından önemli notlar oluştur.
 * 
 * @param {Object} matchResult - Eşleştirme sonucu
 * @returns {string} Koruma notu
 */
function generateConservationNotes(matchResult) {
    if (matchResult.classification === 'EXISTING_RECORD') {
        return (
            `✓ Kayıtlı birey: ${matchResult.matchedTurtleId}. ` +
            `Bu bireyin popülasyon izlemesi devam edecek. ` +
            `Biyometrik takip (non-invasive) sayesinde hayvansal refah korunuyor.`
        );
    } else {
        return (
            `⚠ Yeni birey tespit edildi. Türe göre koruma statüsü kontrol edilmeli. ` +
            `Fotoğrafik biyometri ile izleme başlayacak (metalplaka gereksiz).`
        );
    }
}

/**
 * Express Route Örneği: /api/identify endpoint'e entegrasyon
 * 
 * Kullanım:
 * POST /api/identify
 * {
 *   "photoId": "photo_123",
 *   "biometricVector": [0.45, 0.23, ..., 0.78],  // 128 eleman
 *   "location": "Dalyan Beach",
 *   "captureDate": "2024-01-15T10:30:00Z"
 * }
 */
const express = require('express');
const router = express.Router();

/**
 * Tanımlama ve eşleştirme endpoint'i
 */
router.post('/identify', async (req, res) => {
    try {
        const {
            photoId,
            biometricVector,
            location = 'Unknown',
            captureDate = new Date().toISOString(),
        } = req.body;

        // Girdi validasyonu
        if (!photoId || !biometricVector) {
            return res.status(400).json({
                error: 'Missing required fields: photoId, biometricVector',
            });
        }

        if (!Array.isArray(biometricVector) || biometricVector.length !== 128) {
            return res.status(400).json({
                error: 'biometricVector must be an array of 128 numbers',
            });
        }

        // Matching Agent çalıştır
        const result = await runMatchingAgent({
            photoId,
            biometricVector,
            location,
            captureDate,
        });

        if (!result.success) {
            return res.status(500).json(result);
        }

        // Başarılı sonuç
        res.json({
            success: true,
            identification: result.data,

            // Frontend'e direktif
            action: result.data.matchResult.classification === 'EXISTING_RECORD'
                ? 'SHOW_EXISTING_PROFILE'
                : 'SHOW_NEW_INDIVIDUAL_FORM',

            turtleId: result.data.matchResult.matched_turtle_id,
            confidence: result.data.matchResult.confidence,
        });

    } catch (error) {
        console.error('Identify endpoint error:', error);
        res.status(500).json({
            error: 'Identification failed',
            message: error.message,
        });
    }
});

/**
 * Debug endpoint: Benzerlik hesaplamasını test et
 */
router.post('/debug/match', async (req, res) => {
    try {
        const { biometricVector } = req.body;

        if (!biometricVector || biometricVector.length !== 128) {
            return res.status(400).json({
                error: 'Invalid biometric vector',
            });
        }

        // Top 5 benzer kayıt al
        const alternatives = await SeaTurtleIDMatcher.matchWithAlternatives(
            biometricVector,
            5
        );

        res.json({
            debug: true,
            alternatives: alternatives,
        });

    } catch (error) {
        res.status(500).json({
            error: 'Debug matching failed',
            message: error.message,
        });
    }
});

module.exports = {
    router,
    SeaTurtleIDMatcher,
    runMatchingAgent,
    MATCHING_CONFIG,
};

/**
 * Entegrasyon Adımları:
 * 
 * 1. Backend app.js'e ekle:
 *    const { router: matchingRouter } = require('./agents/matchingAgentWithSeaTurtleID');
 *    app.use('/api', matchingRouter);
 * 
 * 2. Image Analysis Agent'a Python endpoint'i ekle:
 *    - POST /api/match → turtle_matcher.py:TurtleMatcher.match()
 *    - POST /api/match-top-n → turtle_matcher.py:TurtleMatcher.match_with_top_n()
 * 
 * 3. Frontend'den çağrı örneği:
 *    const response = await fetch('/api/identify', {
 *      method: 'POST',
 *      body: JSON.stringify({
 *        photoId: 'photo_123',
 *        biometricVector: extractedVector, // 128-boyutlu array
 *        location: 'Dalyan Beach',
 *        captureDate: new Date().toISOString(),
 *      }),
 *    });
 */
