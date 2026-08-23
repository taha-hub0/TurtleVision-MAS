/**
 * Gatekeeper Agent
 * Sorumluluğu: Gelen fotoğraf isteklerini doğrula (SOLID - SRP)
 * - Metadata validasyonu
 * - GPS koordinat kontrolü
 * - Çekim tarihi doğrulaması
 * - Görüntü formatı kontrolü
 */

const Joi = require('joi');

/**
 * Bir Joi hatasindan okunabilir mesajlar cikar.
 *
 * Neden yardimci bir fonksiyon: `.error(new Error('...'))` kullanildiginda
 * Joi `details` dizisini uretmez, duz bir Error dondurur. O halde
 * `error.details.map(...)` TypeError firlatir ve kullanici alan adi yerine
 * "Cannot read properties of undefined" gorur. Asagidaki savunma, semada
 * ileride ayni hata tekrarlanirsa bile en azindan Error'un kendi mesajini
 * gostermeyi surdurur.
 */
function _mesajlariCikar(error) {
  if (!error) return [];
  if (Array.isArray(error.details) && error.details.length > 0) {
    return error.details.map((d) => d.message);
  }
  return [error.message || 'Validation failed'];
}

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
          .messages({
            'string.base': 'Invalid base64 image: must be a string',
            'string.base64': 'Invalid base64 image: not valid base64',
            'any.required': 'Invalid base64 image: field is required',
          }),
        timestamp: Joi.date()
          .required()
          .max('now')
          .messages({
            'date.base': 'Invalid timestamp: not a valid date',
            'date.max': 'Invalid timestamp: cannot be in the future',
            'any.required': 'Invalid timestamp: field is required',
          }),
      }),

      // GPS koordinatları
      location: Joi.object({
        latitude: Joi.number()
          .min(-90)
          .max(90)
          .required()
          .messages({
            'number.base': 'Invalid latitude: must be a number',
            'number.min': 'Invalid latitude: must be >= -90',
            'number.max': 'Invalid latitude: must be <= 90',
            'any.required': 'Invalid latitude: field is required',
          }),
        longitude: Joi.number()
          .min(-180)
          .max(180)
          .required()
          .messages({
            'number.base': 'Invalid longitude: must be a number',
            'number.min': 'Invalid longitude: must be >= -180',
            'number.max': 'Invalid longitude: must be <= 180',
            'any.required': 'Invalid longitude: field is required',
          }),
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
          .messages({
            'string.base': 'Invalid observer name: must be a string',
            'string.min': 'Invalid observer name: too short (min 2)',
            'string.max': 'Invalid observer name: too long (max 100)',
            'any.required': 'Invalid observer name: field is required',
          }),
        email: Joi.string()
          .email()
          .required()
          .messages({
            'string.base': 'Invalid email: must be a string',
            'string.email': 'Invalid email: not a valid address',
          }),
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
          ..._mesajlariCikar(basicValidation.error)
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
            ..._mesajlariCikar(locationValidation.error)
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
            ..._mesajlariCikar(observerValidation.error)
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
            ..._mesajlariCikar(conditionsValidation.error)
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
