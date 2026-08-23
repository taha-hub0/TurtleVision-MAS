/**
 * Koordinatör ajanlarının birim testleri.
 *
 * Neden var
 * ---------
 * `npm test` daha önce hiç test çalıştırmıyordu: `tests/integration.test.js`
 * aslında elle çalıştırılan, ayakta bir sistem gerektiren bir betikti ama
 * `.test.js` uzantısı yüzünden jest onu topluyor ve "en az bir test içermeli"
 * diyerek düşüyordu. Yani test paketi hem boştu hem kırmızıydı.
 *
 * Buradaki testler ağ, veritabanı ya da model gerektirmez; saf mantığı
 * doğrular ve saniyeler içinde çalışır.
 */

const gatekeeper = require('../src/agents/gatekeeperAgent');
const matcher = require('../src/agents/matchingAgent');

/** Geçerli, küçük bir base64 PNG. */
const GECERLI_PNG =
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';

/** Tüm alanları dolu, doğrulamayı geçmesi beklenen metadata. */
function gecerliMetadata(ustuneYaz = {}) {
  return {
    imageBase64: GECERLI_PNG,
    timestamp: new Date(Date.now() - 60_000).toISOString(),
    location: { latitude: 37.7, longitude: 20.9, accuracy: 5 },
    observer: { name: 'Saha Ekibi', email: 'saha@ornek.org' },
    conditions: { waterTemperature: 22, weather: 'sunny' },
    ...ustuneYaz,
  };
}

describe('GatekeeperAgent — metadata doğrulama', () => {
  test('geçerli metadata kabul edilir', async () => {
    const r = await gatekeeper.validateMetadata(gecerliMetadata());
    expect(r.errors).toEqual([]);
    expect(r.success).toBe(true);
    expect(r.data.validatedAt).toBeDefined();
  });

  test('GPS yoksa reddedilir', async () => {
    const m = gecerliMetadata();
    delete m.location;
    const r = await gatekeeper.validateMetadata(m);
    expect(r.success).toBe(false);
    expect(r.errors).toContain('GPS location is required');
  });

  test('aralık dışı enlem reddedilir', async () => {
    const r = await gatekeeper.validateMetadata(
      gecerliMetadata({ location: { latitude: 91, longitude: 20.9 } })
    );
    expect(r.success).toBe(false);
    expect(r.errors.length).toBeGreaterThan(0);
  });

  test('aralık dışı boylam reddedilir', async () => {
    const r = await gatekeeper.validateMetadata(
      gecerliMetadata({ location: { latitude: 37.7, longitude: 181 } })
    );
    expect(r.success).toBe(false);
  });

  test('gelecek tarihli çekim reddedilir', async () => {
    const yarin = new Date(Date.now() + 86_400_000).toISOString();
    const r = await gatekeeper.validateMetadata(gecerliMetadata({ timestamp: yarin }));
    expect(r.success).toBe(false);
  });

  test('gözlemci bilgisi eksikse uyarı verilir ama reddedilmez', async () => {
    const m = gecerliMetadata();
    delete m.observer;
    const r = await gatekeeper.validateMetadata(m);
    expect(r.success).toBe(true);
    expect(r.warnings).toContain('Observer information not provided');
  });

  test('doğrulama hata mesajı üretebilmeli, çökmemeli', async () => {
    // Joi şemasında `.error(new Error(...))` kullanılırsa doğrulama
    // hatası `error.details` yerine bir istisna olarak gelir; kod
    // `error.details.map(...)` çağırdığı için TypeError'a düşer ve
    // kullanıcı "Validation error: Cannot read properties of undefined"
    // gibi anlamsız bir mesaj alır. Mesajın alan hakkında bir şey
    // söylemesi gerekir.
    const r = await gatekeeper.validateMetadata(
      gecerliMetadata({ location: { latitude: 91, longitude: 20.9 } })
    );
    expect(r.errors.join(' ')).not.toMatch(/Cannot read propert/i);
    expect(r.errors.join(' ')).toMatch(/latitude/i);
  });

  test('prepareMetadata veritabanı biçimine çevirir', async () => {
    const r = await gatekeeper.validateMetadata(gecerliMetadata());
    const db = gatekeeper.prepareMetadata(r.data);
    expect(db.latitude).toBe(37.7);
    expect(db.longitude).toBe(20.9);
    expect(db.observer_name).toBe('Saha Ekibi');
    expect(db.captured_at).toBe(r.data.timestamp);
  });

  test('getHealth ajan kimliğini bildirir', () => {
    const h = gatekeeper.getHealth();
    expect(h.agent).toBe('GatekeeperAgent');
    expect(h.status).toBe('healthy');
  });
});

describe('MatchingAgent — benzerlik hesapları', () => {
  test('Hamming: özdeş kodlar tam benzerlik verir', () => {
    const r = matcher.calculateHammingDistance('10110', '10110');
    expect(r.distance).toBe(0);
    expect(r.similarity).toBe(1);
  });

  test('Hamming: her bit farkı sayılır', () => {
    const r = matcher.calculateHammingDistance('10110', '10011');
    expect(r.distance).toBe(2);
    expect(r.similarity).toBeCloseTo(0.6, 5);
  });

  test('Hamming: farklı uzunluklar karşılaştırılamaz', () => {
    const r = matcher.calculateHammingDistance('101', '10110');
    expect(r.similarity).toBe(0);
    expect(r.distance).toBe(Number.MAX_VALUE);
  });

  test('kosinüs: aynı yönlü vektörler 1 verir', () => {
    expect(matcher.calculateCosineSimilarity([1, 0, 0], [2, 0, 0])).toBeCloseTo(1, 6);
  });

  test('kosinüs: dik vektörler 0 verir', () => {
    expect(matcher.calculateCosineSimilarity([1, 0], [0, 1])).toBeCloseTo(0, 6);
  });

  test('kosinüs: zıt vektörler -1 verir', () => {
    expect(matcher.calculateCosineSimilarity([1, 0], [-1, 0])).toBeCloseTo(-1, 6);
  });

  test('kosinüs: sıfır vektör bölme hatası vermez', () => {
    expect(matcher.calculateCosineSimilarity([0, 0], [1, 1])).toBe(0);
  });

  test('rapor: kayıtlı birey EXISTING_RECORD üretir', () => {
    const rapor = matcher.generateMatchReport({
      classification: 'EXISTING_RECORD',
      confidence: 0.93,
      topMatch: { turtle_id: 'T001' },
      matchMethod: 'cosine',
      matches: [],
    });
    expect(rapor.details.type).toBe('ESKI_KAYIT');
    expect(rapor.details.similarity).toBe('93.00%');
  });

  test('rapor: yeni birey yalnızca güçlü adayları listeler', () => {
    const rapor = matcher.generateMatchReport({
      classification: 'NEW_INDIVIDUAL',
      confidence: 0.4,
      matches: [
        { turtle_id: 'T009', similarity: 0.75 },
        { turtle_id: 'T014', similarity: 0.4 },
      ],
    });
    expect(rapor.details.possibleMatches).toHaveLength(1);
    expect(rapor.details.closestMatch.turtle_id).toBe('T009');
  });

  test('getHealth ajan kimliğini bildirir', () => {
    expect(matcher.getHealth().agent).toBe('MatchingAgent');
  });
});
