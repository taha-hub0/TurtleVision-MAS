const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');
const matchingAgent = require('../agents/matchingAgent');
const agentService = require('../services/agentService');

/**
 * POST /api/matching/find
 * Matching Agent: Biyometrik kodu veritabanında ara
 * Görev: %90 benzerlik kuralı ile eski kayıt/yeni birey sınıflandırması
 */
router.post('/find', async (req, res) => {
  const requestId = uuidv4();

  try {
    const { biometricCode, matchingCriteria = {} } = req.body;

    if (!biometricCode) {
      return res.status(400).json({
        success: false,
        error: 'Missing biometricCode',
        requestId,
      });
    }

    console.log(`[${requestId}] Starting similarity matching...`);

    // Matching Agent ile veritabanında ara
    // Not: DB Agent'dan getAllTurtlesBiometrics() metodu gerekir
    // Örnek implementasyon:
    const matchResult = await matchingAgent.findMatchInDatabase(
      biometricCode,
      {
        getAllTurtlesBiometrics: async () => {
          // Bu method database-agent'tan gelecek
          return await agentService.getAllTurtlesBiometrics();
        },
      },
      matchingCriteria
    );

    // Matching raporu oluştur
    const report = matchingAgent.generateMatchReport(matchResult, {});

    res.status(200).json({
      success: true,
      requestId,
      matching_result: matchResult,
      report,
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error(`[${requestId}] Matching error:`, error);
    res.status(500).json({
      success: false,
      error: error.message,
      requestId,
    });
  }
});

/**
 * POST /api/matching/batch
 * Birden fazla kodu eşzamanlı olarak eşleştir
 */
router.post('/batch', async (req, res) => {
  const requestId = uuidv4();

  try {
    const { biometricCodes = [], matchingCriteria = {} } = req.body;

    if (!Array.isArray(biometricCodes) || biometricCodes.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Missing biometricCodes array',
        requestId,
      });
    }

    console.log(
      `[${requestId}] Batch matching ${biometricCodes.length} codes...`
    );

    const results = [];

    for (const code of biometricCodes) {
      try {
        const matchResult = await matchingAgent.findMatchInDatabase(
          code,
          {
            getAllTurtlesBiometrics: async () => {
              return await agentService.getAllTurtlesBiometrics();
            },
          },
          matchingCriteria
        );

        results.push({
          biometric_code: code,
          result: matchResult,
        });
      } catch (error) {
        results.push({
          biometric_code: code,
          error: error.message,
        });
      }
    }

    res.status(200).json({
      success: true,
      requestId,
      batch_size: biometricCodes.length,
      results,
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error(`[${requestId}] Batch matching error:`, error);
    res.status(500).json({
      success: false,
      error: error.message,
      requestId,
    });
  }
});

/**
 * GET /api/matching/health
 * Matching Agent sağlık kontrolü
 */
router.get('/health', (req, res) => {
  try {
    const health = matchingAgent.getHealth();
    res.status(200).json(health);
  } catch (error) {
    res.status(500).json({
      error: error.message,
    });
  }
});

module.exports = router;
