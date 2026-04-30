/**
 * Gatekeeper Agent
 * Sorumluluğu: Gelen fotoğraf isteklerini doğrula (SOLID - SRP)
 * - Metadata validasyonu
 * - GPS koordinat kontrolü
 * - Çekim tarihi doğrulaması
 * - Görüntü formatı kontrolü
 */

const Joi = require('joi');

class GatekeeperAgent {
  constructor() {
    this.name = 'GatekeeperAgent';
    this.version = '1.0.0';
    this.validationSchema = this._initializeSchema();
  }

  /**
   * Validasyon şemasını başlat (SOLID - Interface Segregation)
   */
  _initializeSchema() {
    return {
      // Temel metadata
      basic: Joi.object({
        imageBase64: Joi.string()
          .required()
          .base64()
          .error(new Error('Invalid base64 image')),
        timestamp: Joi.date()
          .required()
          .max('now')
          .error(new Error('Invalid timestamp')),
      }),

      // GPS koordinatları
      location: Joi.object({
        latitude: Joi.number()
          .min(-90)
          .max(90)
          .required()
          .error(new Error('Invalid latitude')),
        longitude: Joi.number()
          .min(-180)
          .max(180)
          .required()
          .error(new Error('Invalid longitude')),
        accuracy: Joi.number()
          .min(0)
          .max(10000)
          .optional(),
      }),

      // Gözlemci bilgileri
      observer: Joi.object({
        name: Joi.string()
          .min(2)
          .max(100)
          .required()
          .error(new Error('Invalid observer name')),
        email: Joi.string()
          .email()
          .required()
          .error(new Error('Invalid email')),
        organization: Joi.string()
          .max(200)
          .optional(),
      }),

      // Çekim koşulları
      conditions: Joi.object({
        waterTemperature: Joi.number()
          .min(0)
          .max(40)
          .optional(),
        weather: Joi.string()
          .valid('sunny', 'cloudy', 'rainy', 'stormy')
          .optional(),
        waterClarity: Joi.string()
          .valid('clear', 'turbid', 'murky')
          .optional(),
      }),
    };
  }

  /**
   * Tüm metadata'yı doğrula (SOLID - Open/Closed: yeni validasyon eklenebilir)
   */
  async validateMetadata(metadata) {
    const validationResult = {
      success: false,
      errors: [],
      warnings: [],
      data: null,
    };

    try {
      // 1. Temel alan doğrulaması
      const basicValidation = this.validationSchema.basic.validate(
        {
          imageBase64: metadata.imageBase64,
          timestamp: new Date(metadata.timestamp),
        },
        { abortEarly: false }
      );

      if (basicValidation.error) {
        validationResult.errors.push(
          ...basicValidation.error.details.map((d) => d.message)
        );
        return validationResult;
      }

      // 2. GPS koordinat doğrulaması
      if (metadata.location) {
        const locationValidation = this.validationSchema.location.validate(
          metadata.location,
          { abortEarly: false }
        );

        if (locationValidation.error) {
          validationResult.errors.push(
            ...locationValidation.error.details.map((d) => d.message)
          );
          return validationResult;
        }
      } else {
        validationResult.errors.push('GPS location is required');
        return validationResult;
      }

      // 3. Gözlemci bilgileri doğrulaması
      if (metadata.observer) {
        const observerValidation = this.validationSchema.observer.validate(
          metadata.observer,
          { abortEarly: false }
        );

        if (observerValidation.error) {
          validationResult.errors.push(
            ...observerValidation.error.details.map((d) => d.message)
          );
          return validationResult;
        }
      } else {
        validationResult.warnings.push('Observer information not provided');
      }

      // 4. Çekim koşulları doğrulaması
      if (metadata.conditions) {
        const conditionsValidation = this.validationSchema.conditions.validate(
          metadata.conditions,
          { abortEarly: false }
        );

        if (conditionsValidation.error) {
          validationResult.warnings.push(
            ...conditionsValidation.error.details.map((d) => d.message)
          );
        }
      }

      // 5. Görüntü boyutu kontrolü
      if (!this._validateImageSize(metadata.imageBase64)) {
        validationResult.errors.push('Image size exceeds 50MB limit');
        return validationResult;
      }

      // 6. Çekim tarihi mantığı kontrolü
      const captureDate = new Date(metadata.timestamp);
      if (captureDate > new Date()) {
        validationResult.errors.push('Capture date cannot be in the future');
        return validationResult;
      }

      // Tüm doğrulamalar başarılı
      validationResult.success = true;
      validationResult.data = {
        imageBase64: metadata.imageBase64,
        timestamp: metadata.timestamp,
        location: metadata.location,
        observer: metadata.observer || {},
        conditions: metadata.conditions || {},
        validatedAt: new Date().toISOString(),
      };

      return validationResult;
    } catch (error) {
      validationResult.errors.push(`Validation error: ${error.message}`);
      return validationResult;
    }
  }

  /**
   * Görüntü boyutu kontrolü (50MB limit)
   */
  _validateImageSize(imageBase64) {
    try {
      // Base64 string'in boyutu yaklaşık olarak
      const sizeInBytes = Buffer.byteLength(imageBase64, 'utf8');
      const maxSizeInBytes = 50 * 1024 * 1024; // 50MB
      return sizeInBytes <= maxSizeInBytes;
    } catch {
      return false;
    }
  }

  /**
   * Doğrulanmış metadata'yı veritabanına kaydedilecek formata dönüştür
   */
  prepareMetadata(validatedData) {
    return {
      captured_at: validatedData.timestamp,
      latitude: validatedData.location.latitude,
      longitude: validatedData.location.longitude,
      accuracy: validatedData.location.accuracy || null,
      observer_name: validatedData.observer.name || 'Unknown',
      observer_email: validatedData.observer.email || null,
      organization: validatedData.observer.organization || null,
      water_temperature: validatedData.conditions.waterTemperature || null,
      weather: validatedData.conditions.weather || null,
      water_clarity: validatedData.conditions.waterClarity || null,
      validated_at: validatedData.validatedAt,
    };
  }

  /**
   * Agent sağlık kontrolü
   */
  getHealth() {
    return {
      agent: this.name,
      version: this.version,
      status: 'healthy',
      timestamp: new Date().toISOString(),
    };
  }
}

module.exports = new GatekeeperAgent();
