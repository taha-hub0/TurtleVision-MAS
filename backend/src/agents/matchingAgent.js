/**
 * Matching Agent
 * Sorumluluğu: Biyometrik kodları veritabanı kayıtlarıyla karşılaştır
 * - %90 benzerlik kuralı
 * - Eski kayıt vs Yeni birey sınıflandırması
 * - Hamming distance hesaplaması (SOLID - SRP)
 */

class MatchingAgent {
  constructor() {
    this.name = 'MatchingAgent';
    this.version = '1.0.0';
    this.similarityThreshold = 0.9; // %90 benzerlik
  }

  /**
   * Iki biyometrik kod arasındaki Hamming distance'ı hesapla
   * Düşük distance = yüksek benzerlik
   */
  calculateHammingDistance(code1, code2) {
    if (code1.length !== code2.length) {
      return {
        distance: Number.MAX_VALUE,
        similarity: 0,
      };
    }

    let distance = 0;
    for (let i = 0; i < code1.length; i++) {
      if (code1[i] !== code2[i]) {
        distance++;
      }
    }

    const similarity = 1 - distance / code1.length;

    return {
      distance,
      similarity: Math.round(similarity * 100) / 100,
    };
  }

  /**
   * Kosinüs benzerliği (alternatif metod)
   */
  calculateCosineSimilarity(vector1, vector2) {
    const dotProduct = vector1.reduce((sum, a, i) => sum + a * vector2[i], 0);
    const magnitude1 = Math.sqrt(vector1.reduce((sum, a) => sum + a * a, 0));
    const magnitude2 = Math.sqrt(vector2.reduce((sum, a) => sum + a * a, 0));

    if (magnitude1 === 0 || magnitude2 === 0) {
      return 0;
    }

    return dotProduct / (magnitude1 * magnitude2);
  }

  /**
   * Biyometrik kodu veritabanında eş kayıt ara
   * (SOLID - Dependency Inversion: dbAgent'a bağımlı)
   */
  async findMatchInDatabase(biometricCode, dbAgent, matchingCriteria = {}) {
    const {
      threshold = this.similarityThreshold,
      topN = 5,
      method = 'hamming',
    } = matchingCriteria;

    try {
      // Veritabanından tüm kayıtlı kaplumbağaların kodlarını al
      const allRecords = await dbAgent.getAllTurtlesBiometrics();

      if (!allRecords || allRecords.length === 0) {
        return {
          success: true,
          classification: 'NEW_INDIVIDUAL',
          matches: [],
          topMatch: null,
          reason: 'No records in database',
        };
      }

      // Her kayıtla benzerlik hesapla
      const similarities = allRecords.map((record) => {
        let similarity;

        if (method === 'hamming' && typeof biometricCode === 'string') {
          // String tabanlı Hamming distance
          const result = this.calculateHammingDistance(
            biometricCode,
            record.biometric_code
          );
          similarity = result.similarity;
        } else if (method === 'cosine' && Array.isArray(biometricCode)) {
          // Vector tabanlı kosinüs benzerliği
          similarity = this.calculateCosineSimilarity(
            biometricCode,
            record.biometric_vector
          );
        } else {
          similarity = 0;
        }

        return {
          turtleId: record.turtle_id,
          species: record.species,
          recordedAt: record.registered_at,
          similarity,
        };
      });

      // Benzerliğe göre sırala
      similarities.sort((a, b) => b.similarity - a.similarity);

      // En iyi eşleşmeyi kontrol et
      const topMatch = similarities[0];
      const isMatch = topMatch.similarity >= threshold;

      // En iyi N eşleşmeyi al
      const topMatches = similarities.slice(0, topN);

      return {
        success: true,
        classification: isMatch ? 'EXISTING_RECORD' : 'NEW_INDIVIDUAL',
        matches: topMatches,
        topMatch: isMatch ? topMatch : null,
        confidence: isMatch ? topMatch.similarity : 0,
        threshold: threshold,
        matchMethod: method,
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        classification: 'UNKNOWN',
      };
    }
  }

  /**
   * Matching sonucunu analiz ve rapor et
   */
  generateMatchReport(matchResult, turtleData) {
    const report = {
      timestamp: new Date().toISOString(),
      classification: matchResult.classification,
      confidence: matchResult.confidence,
      details: {},
    };

    if (matchResult.classification === 'EXISTING_RECORD') {
      report.details = {
        type: 'ESKI_KAYIT',
        description: 'Previously identified individual',
        matchedTurtle: matchResult.topMatch,
        matchingMethod: matchResult.matchMethod,
        similarity: `${(matchResult.confidence * 100).toFixed(2)}%`,
      };
    } else {
      report.details = {
        type: 'YENİ_BİREY',
        description: 'New individual detected',
        possibleMatches: matchResult.matches.filter((m) => m.similarity > 0.7),
        closestMatch: matchResult.matches[0],
      };
    }

    return report;
  }

  /**
   * Agent sağlık kontrolü
   */
  getHealth() {
    return {
      agent: this.name,
      version: this.version,
      status: 'healthy',
      threshold: this.similarityThreshold,
      timestamp: new Date().toISOString(),
    };
  }
}

module.exports = new MatchingAgent();
