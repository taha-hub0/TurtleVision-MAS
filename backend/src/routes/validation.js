const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');
const gatekeeperAgent = require('../agents/gatekeeperAgent');

/**
 * POST /api/validation/validate
 * Gatekeeper Agent: Metadata doğrulaması
 * Görev: GPS, tarih, gözlemci bilgisini kontrol et
 */
router.post('/validate', async (req, res) => {
  const requestId = uuidv4();
  
  try {
    const metadata = req.body;

    if (!metadata) {
      return res.status(400).json({
        success: false,
        error: 'Missing metadata',
        requestId,
      });
    }

    // Gatekeeper Agent tarafından doğrula
    const validationResult = await gatekeeperAgent.validateMetadata(metadata);

    if (!validationResult.success) {
      return res.status(400).json({
        success: false,
        errors: validationResult.errors,
        warnings: validationResult.warnings,
        requestId,
        timestamp: new Date().toISOString(),
      });
    }

    // Doğrulanan metadata'yı formatla
    const preparedMetadata = gatekeeperAgent.prepareMetadata(
      validationResult.data
    );

    res.status(200).json({
      success: true,
      requestId,
      validated_metadata: preparedMetadata,
      warnings: validationResult.warnings,
      validated_at: new Date().toISOString(),
    });

  } catch (error) {
    console.error(`[${requestId}] Validation error:`, error);
    res.status(500).json({
      success: false,
      error: error.message,
      requestId,
    });
  }
});

/**
 * GET /api/validation/health
 * Gatekeeper Agent sağlık kontrolü
 */
router.get('/health', (req, res) => {
  try {
    const health = gatekeeperAgent.getHealth();
    res.status(200).json(health);
  } catch (error) {
    res.status(500).json({
      error: error.message,
    });
  }
});

module.exports = router;
