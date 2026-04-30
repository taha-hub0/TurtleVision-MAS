const express = require('express');
const router = express.Router();
const agentService = require('../services/agentService');

/**
 * GET /api/health
 * Sistem durumu kontrolü
 */
router.get('/', async (req, res) => {
    try {
        const imageAgentHealthy = await agentService.checkImageAnalysisAgent();
        const dbAgentHealthy = await agentService.checkDatabaseAgent();

        const systemHealth = {
            coordinator: 'OK',
            imageAnalysisAgent: imageAgentHealthy ? 'OK' : 'FAILED',
            databaseAgent: dbAgentHealthy ? 'OK' : 'FAILED',
            timestamp: new Date().toISOString(),
            allAgentsHealthy: imageAgentHealthy && dbAgentHealthy
        };

        res.status(systemHealth.allAgentsHealthy ? 200 : 503).json(systemHealth);
    } catch (error) {
        res.status(500).json({
            error: 'Health check failed',
            message: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

module.exports = router;
