const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');
const agentService = require('../services/agentService');

/**
 * POST /api/identification/identify
 * Yüklenen görüntüden kaplumbağa tanımlama
 */
router.post('/identify', async (req, res) => {
    const requestId = uuidv4();

    try {
        const { imageBase64, metadata = {} } = req.body;

        if (!imageBase64) {
            return res.status(400).json({
                error: 'Missing imageBase64',
                requestId
            });
        }

        console.log(`[${requestId}] Starting turtle identification...`);

        // Step 1: Görüntü analiz iste
        console.log(`[${requestId}] Sending image to analysis agent...`);
        const analysisResult = await agentService.identifyTurtle(imageBase64, metadata);

        if (!analysisResult.success) {
            return res.status(400).json({
                error: 'Image analysis failed',
                requestId,
                details: analysisResult.error
            });
        }

        // Step 2: Benzer kaplumbağaları ara
        console.log(`[${requestId}] Searching for similar turtles...`);
        const similarTurtles = await agentService.findSimilarTurtles(
            analysisResult,
            0.85
        );

        // Step 3: Sonuç oluştur
        const result = {
            requestId,
            success: true,
            identification: analysisResult,
            similarMatches: similarTurtles.matches || [],
            confidence: analysisResult.confidence,
            timestamp: new Date().toISOString()
        };

        console.log(`[${requestId}] Identification completed successfully`);
        res.status(200).json(result);

    } catch (error) {
        console.error(`[${requestId}] Error:`, error.message);
        res.status(500).json({
            error: 'Identification failed',
            requestId,
            message: error.message
        });
    }
});

/**
 * POST /api/identification/register
 * Yeni tanımlanan kaplumbağa kaydetme
 */
router.post('/register', async (req, res) => {
    const requestId = uuidv4();

    try {
        const { imageBase64, analysisResult, metadata = {} } = req.body;

        if (!imageBase64 || !analysisResult) {
            return res.status(400).json({
                error: 'Missing required fields: imageBase64, analysisResult',
                requestId
            });
        }

        console.log(`[${requestId}] Registering new turtle...`);

        // Veritabanında kaydını yap
        const turtleData = {
            id: uuidv4(),
            imageBase64,
            analysisResult,
            metadata,
            registeredAt: new Date().toISOString()
        };

        const dbResult = await agentService.saveTurtleToDatabase(turtleData);

        res.status(201).json({
            success: true,
            requestId,
            turtle: dbResult,
            message: 'Turtle registered successfully'
        });

    } catch (error) {
        console.error(`[${requestId}] Error:`, error.message);
        res.status(500).json({
            error: 'Registration failed',
            requestId,
            message: error.message
        });
    }
});

module.exports = router;
