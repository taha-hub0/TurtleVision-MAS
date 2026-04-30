const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');
const reporterAgent = require('../agents/reporterAgent');

/**
 * POST /api/reporting/generate
 * Reporter Agent: JSON/PDF rapor üret
 * Görev: DEKAMER standartlarında rapor
 */
router.post('/generate', async (req, res) => {
  const requestId = uuidv4();

  try {
    const { analysisData, matchingData, format = 'json' } = req.body;

    if (!analysisData || !matchingData) {
      return res.status(400).json({
        success: false,
        error: 'Missing analysisData or matchingData',
        requestId,
      });
    }

    console.log(`[${requestId}] Generating ${format} report...`);

    let report;

    if (format === 'json') {
      // JSON rapor oluştur
      report = reporterAgent.generateJSONReport(analysisData, matchingData);

      res.status(200).json({
        success: true,
        requestId,
        format: 'json',
        report,
        timestamp: new Date().toISOString(),
      });

    } else if (format === 'pdf') {
      // Önce JSON rapor oluştur
      const jsonReport = reporterAgent.generateJSONReport(
        analysisData,
        matchingData
      );

      // Sonra PDF'ye dönüştür
      try {
        const pdfResult = await reporterAgent.generatePDFReport(jsonReport);

        res.status(200).json({
          success: true,
          requestId,
          format: 'pdf',
          report_id: pdfResult.report_id,
          filename: pdfResult.filename,
          filepath: pdfResult.filepath,
          timestamp: new Date().toISOString(),
        });
      } catch (pdfError) {
        console.warn('PDF generation not available, returning JSON instead');
        res.status(200).json({
          success: true,
          requestId,
          format: 'json',
          report: jsonReport,
          note: 'PDF generation not available, JSON report returned',
          timestamp: new Date().toISOString(),
        });
      }

    } else {
      return res.status(400).json({
        success: false,
        error: `Unsupported format: ${format}. Use 'json' or 'pdf'`,
        requestId,
      });
    }

  } catch (error) {
    console.error(`[${requestId}] Report generation error:`, error);
    res.status(500).json({
      success: false,
      error: error.message,
      requestId,
    });
  }
});

/**
 * GET /api/reporting/report/:reportId
 * Rapor getir
 */
router.get('/report/:reportId', async (req, res) => {
  try {
    const { reportId } = req.params;
    const { format = 'json' } = req.query;

    const report = reporterAgent.getReport(reportId, format);

    res.status(200).json({
      success: true,
      report,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * GET /api/reporting/health
 * Reporter Agent sağlık kontrolü
 */
router.get('/health', (req, res) => {
  try {
    const health = reporterAgent.getHealth();
    res.status(200).json(health);
  } catch (error) {
    res.status(500).json({
      error: error.message,
    });
  }
});

module.exports = router;
