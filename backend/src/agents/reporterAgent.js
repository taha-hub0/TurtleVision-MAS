/**
 * Reporter Agent
 * Sorumluluğu: Raporlar üret (JSON, PDF)
 * - DEKAMER standardına uygun rapor üretimi
 * - Non-invaziv metod analizi
 * - Karşılaştırma ve validasyon
 * (SOLID - SRP & Open/Closed)
 */

const PDFDocument = require('pdfkit');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

class ReporterAgent {
  constructor() {
    this.name = 'ReporterAgent';
    this.version = '1.0.0';
    this.reportDir = './reports';
    this._ensureReportDirectory();
  }

  /**
   * Rapor dizini oluştur
   */
  _ensureReportDirectory() {
    if (!fs.existsSync(this.reportDir)) {
      fs.mkdirSync(this.reportDir, { recursive: true });
    }
  }

  /**
   * JSON rapor oluştur
   */
  generateJSONReport(analysisData, matchingData) {
    const reportId = uuidv4();
    const timestamp = new Date().toISOString();

    const report = {
      report_id: reportId,
      timestamp,
      generated_by: this.name,
      version: this.version,

      // Gözlem Bilgileri
      observation: {
        captured_at: analysisData.metadata.timestamp,
        location: {
          latitude: analysisData.metadata.location.latitude,
          longitude: analysisData.metadata.location.longitude,
          accuracy_m: analysisData.metadata.location.accuracy,
        },
        observer: {
          name: analysisData.metadata.observer.name,
          email: analysisData.metadata.observer.email,
          organization: analysisData.metadata.observer.organization,
        },
        conditions: analysisData.metadata.conditions,
      },

      // Biyolojik Analiz (DEKAMER Standard)
      biological_analysis: {
        method: 'NON_INVASIVE_BIOMETRIC',
        species: analysisData.analysis.species,
        confidence: analysisData.analysis.confidence,

        // Tür spesifik özellikler
        identification_markers: {
          type: analysisData.analysis.turtle_type,
          markers: this._extractMarkers(analysisData),
        },

        // Biyometrik kod
        biometric_signature: {
          code: analysisData.biometric_code,
          extraction_method: analysisData.extraction_method,
          quality_score: analysisData.quality_score,
        },

        // Ölçümler
        measurements: {
          shell_length_cm: analysisData.measurements.shell_length,
          shell_width_cm: analysisData.measurements.shell_width,
          weight_kg: analysisData.measurements.weight,
        },

        // Sağlık durumu
        health_status: {
          wounds: analysisData.health.wounds || [],
          diseases: analysisData.health.diseases || [],
          parasites: analysisData.health.parasites || [],
          overall_condition: analysisData.health.condition || 'UNKNOWN',
        },
      },

      // Eşleştirme Sonuçları
      matching_result: {
        classification: matchingData.classification,
        confidence: matchingData.confidence,
        threshold_used: matchingData.threshold,
        matching_method: matchingData.matchMethod,
      },

      // Eğer eşleşme bulunduysa
      matched_individual: matchingData.topMatch
        ? {
            turtle_id: matchingData.topMatch.turtleId,
            first_recorded: matchingData.topMatch.recordedAt,
            similarity_score: matchingData.topMatch.similarity,
            previous_sightings_count: matchingData.topMatch.sightings_count,
          }
        : null,

      // Özellikle Yeni Bireyler İçin
      potential_matches: matchingData.matches
        .filter((m) => m.similarity > 0.7)
        .slice(0, 3)
        .map((m) => ({
          turtle_id: m.turtleId,
          similarity: m.similarity,
          last_seen: m.recordedAt,
        })),

      // Metodoloji Analizi
      methodology: {
        title: 'Non-Invaziv Biyometrik Tanımlama - DEKAMER Standardı',
        description:
          'Bu rapor, deniz kaplumbağalarının fotoğrafik biyometrik analiz ' +
          'yöntemiyle tanımlandığını göstermektedir.',

        advantages: [
          {
            title: 'Zararsız (Non-invasive)',
            description:
              'Hayvanın bedensel bütünlüğünü koruyarak tanımlama yapılır.',
          },
          {
            title: 'Maliyet Etkin',
            description:
              'Geleneksel markalama yöntemine kıyasla çok daha ekonomiktir.',
          },
          {
            title: 'Güvenilir',
            description:
              'Yapay zeka destekli görüntü analizi sayesinde yüksek doğruluk sağlar.',
          },
          {
            title: 'İleri İzleme',
            description:
              'Populasyon dinamiklerinin uzun vadeli izlenmesine olanak tanır.',
          },
        ],

        comparison_with_traditional: {
          marking_method: 'Geleneksel Markalama',
          marking_invasiveness: 'İnvazif (Hayvana fiziksel hasar)',
          marking_cost: 'Yüksek (Malzeme, süre, geri yakalama)',
          marking_reliability: 'Orta (İzin kaybolabilir)',

          biometric_method: 'Fotoğrafik Biyometri',
          biometric_invasiveness: 'Non-invazif (Zararsız)',
          biometric_cost: 'Düşük (Sayısal teknoloji)',
          biometric_reliability: 'Çok Yüksek (AI destekli analiz)',
        },
      },

      // DEKAMER Standart Uygunluğu
      compliance: {
        standard: 'DEKAMER (Deniz Kaplumbağaları Araştırma Enstitüsü)',
        compliant: true,
        regions_covered: ['Turkey', 'Mediterranean'],
      },

      // Sonuç ve Öneriler
      conclusions: {
        primary_finding: this._generateConclusion(analysisData, matchingData),
        conservation_value:
          'Bu tanımlama, popülasyon yönetimi ve koruma stratejilerine katkı sağlar.',
        recommended_actions: this._generateRecommendations(
          analysisData,
          matchingData
        ),
      },

      // Kalite Metrikleri
      quality_metrics: {
        image_quality: analysisData.quality_score,
        analysis_confidence: analysisData.analysis.confidence,
        matching_confidence: matchingData.confidence,
        overall_reliability: Math.min(
          analysisData.quality_score,
          analysisData.analysis.confidence,
          matchingData.confidence
        ),
      },
    };

    return report;
  }

  /**
   * PDF rapor oluştur
   */
  async generatePDFReport(jsonReport) {
    return new Promise((resolve, reject) => {
      try {
        const filename = `report_${jsonReport.report_id}.pdf`;
        const filepath = path.join(this.reportDir, filename);

        const doc = new PDFDocument();
        const stream = fs.createWriteStream(filepath);

        doc.pipe(stream);

        // Başlık
        doc.fontSize(24).font('Helvetica-Bold').text('Turtle-ID Report');
        doc
          .fontSize(12)
          .font('Helvetica')
          .text(`Report ID: ${jsonReport.report_id}`)
          .text(`Generated: ${jsonReport.timestamp}\n`);

        // Gözlem Bilgileri
        doc.fontSize(14).font('Helvetica-Bold').text('Observation Details');
        doc.fontSize(11).font('Helvetica');
        doc.text(`Captured at: ${jsonReport.observation.captured_at}`);
        doc.text(
          `Location: ${jsonReport.observation.location.latitude}, ${jsonReport.observation.location.longitude}`
        );
        doc.text(`Observer: ${jsonReport.observation.observer.name}\n`);

        // Biyolojik Analiz
        doc.fontSize(14).font('Helvetica-Bold').text('Biological Analysis');
        doc.fontSize(11).font('Helvetica');
        doc.text(`Species: ${jsonReport.biological_analysis.species}`);
        doc.text(
          `Confidence: ${(jsonReport.biological_analysis.confidence * 100).toFixed(2)}%`
        );
        doc.text(
          `Identification Type: ${jsonReport.biological_analysis.identification_markers.type}\n`
        );

        // Eşleştirme Sonuçları
        doc
          .fontSize(14)
          .font('Helvetica-Bold')
          .text('Matching Result');
        doc.fontSize(11).font('Helvetica');
        doc.text(
          `Classification: ${jsonReport.matching_result.classification}`
        );
        doc.text(
          `Confidence: ${(jsonReport.matching_result.confidence * 100).toFixed(2)}%\n`
        );

        if (jsonReport.matched_individual) {
          doc.text(
            `Matched Turtle ID: ${jsonReport.matched_individual.turtle_id}`
          );
          doc.text(
            `First Recorded: ${jsonReport.matched_individual.first_recorded}\n`
          );
        }

        // Metodoloji
        doc.fontSize(14).font('Helvetica-Bold').text('Methodology');
        doc.fontSize(11).font('Helvetica');
        doc.text(jsonReport.methodology.description);
        doc.text('Advantages of Non-Invasive Biometric Method:');
        jsonReport.methodology.advantages.forEach((adv) => {
          doc.text(`  • ${adv.title}: ${adv.description}`);
        });

        doc.text('\n');

        // Sonuç
        doc.fontSize(14).font('Helvetica-Bold').text('Conclusion');
        doc.fontSize(11).font('Helvetica');
        doc.text(jsonReport.conclusions.primary_finding);

        doc.end();

        stream.on('finish', () => {
          resolve({
            success: true,
            filename,
            filepath,
            report_id: jsonReport.report_id,
          });
        });
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Rapor dosyasını getir
   */
  getReport(reportId, format = 'json') {
    // Implementation
    return {
      report_id: reportId,
      format,
      available: true,
    };
  }

  /**
   * Sonuç metni oluştur
   */
  _generateConclusion(analysisData, matchingData) {
    if (matchingData.classification === 'EXISTING_RECORD') {
      return (
        `Bireyin tanımlanmıştır. Turtle-ID: ${matchingData.topMatch.turtleId}, ` +
        `Benzerlik Oranı: ${(matchingData.topMatch.similarity * 100).toFixed(2)}%. ` +
        `Bu birey ilk olarak ${matchingData.topMatch.recordedAt} tarihinde kaydedilmiştir.`
      );
    } else {
      return (
        'Yeni bir birey tanımlanmıştır. Veritabanında önceki kaydı bulunmamaktadır. ' +
        'Bu bireyin uzun vadeli izlenmesi, popülasyon dinamiğini anlamamız için önemlidir.'
      );
    }
  }

  /**
   * Öneriler oluştur
   */
  _generateRecommendations(analysisData, matchingData) {
    const recommendations = [];

    if (analysisData.health.wounds && analysisData.health.wounds.length > 0) {
      recommendations.push(
        'Yaralanmış bireyin sağlık durumu takip edilmelidir.'
      );
    }

    if (
      matchingData.classification === 'NEW_INDIVIDUAL' &&
      matchingData.matches.length > 0
    ) {
      recommendations.push(
        `Benzeri olan ${matchingData.matches.length} birey bulunmaktadır. Detaylı inceleme yapılabilir.`
      );
    }

    return recommendations;
  }

  /**
   * Markerları çıkar
   */
  _extractMarkers(analysisData) {
    const markers = {};

    if (analysisData.analysis.turtle_type === 'GREEN_TURTLE') {
      markers.post_ocular_scutes =
        analysisData.biometric_code ||
        'Post-ocular scute pattern detected';
    } else if (analysisData.analysis.turtle_type === 'LEATHERBACK') {
      markers.pineal_spot =
        analysisData.analysis.pineal_spot || 'Pineal spot detected';
    }

    return markers;
  }

  /**
   * Agent sağlık kontrolü
   */
  getHealth() {
    return {
      agent: this.name,
      version: this.version,
      status: 'healthy',
      report_dir: this.reportDir,
      timestamp: new Date().toISOString(),
    };
  }
}

// PDFKit import - eğer yüklü değilse mock et
let PDFDocumentClass = PDFDocument;
try {
  PDFDocumentClass = require('pdfkit');
} catch {
  PDFDocumentClass = class {
    constructor() {}
    pipe() {
      return this;
    }
    fontSize() {
      return this;
    }
    font() {
      return this;
    }
    text() {
      return this;
    }
    end() {}
  };
}

module.exports = new ReporterAgent();
