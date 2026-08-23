"""
Kimlik düzeyinde eşleştirme (multi-shot galeri) testleri.

Neden var
---------
Eşleştirme eskiden **kare** düzeyindeydi: galerideki 875 kaydın her biri
ayrı bir aday sayılıyordu. İki sonucu vardı:

1. Bir bireyin skoru, o bireye ait tek bir karenin skoruydu. Kötü açılı ya
   da bulanık tek bir kare, o bireyi listeden düşürebiliyordu.
2. `match_with_top_n` "en benzer 5 kayıt" döndürüyordu; bunların hepsi aynı
   bireyin 5 karesi olabiliyordu. Operatöre 5 aday göstermesi beklenen
   ekran tek aday göstermiş oluyordu.

Şimdi skorlar bireyde toplanıyor:
    skor = w * (en iyi karenin benzerliği) + (1 - w) * (centroid benzerliği)

Testler sentetik bir galeri kullanır — gerçek `kaggle_db.json` ya da model
checkpoint'i gerektirmez, böylece CI'da da çalışır.

Çalıştırma:
    cd image-analysis-agent && python -m pytest tests/test_matching.py -v
    (pytest yoksa: python tests/test_matching.py)
"""

import os
import sys
import unittest

import numpy as np

AGENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, AGENT_DIR)

from src.matching.turtle_matcher import (  # noqa: E402
    DEFAULT_MAX_WEIGHT, KimlikIndeksi, TurtleMatcher, kimlik_anahtari)


class SahteDB:
    """TurtleMatcher'ın beklediği en küçük galeri arayüzü."""

    def __init__(self, kayitlar):
        self.database = {k['turtle_id']: k for k in kayitlar}

    def get_all_turtles(self):
        return list(self.database.values())

    def get_turtle_by_id(self, turtle_id):
        return self.database.get(turtle_id)


def birim(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v)


def kayit(turtle_id, identity, vec):
    return {
        'turtle_id': turtle_id,
        'identity': identity,
        'species': 'Caretta caretta',
        'first_recorded': '2022-01-01',
        'biometric_vector': [float(x) for x in birim(vec)],
    }


def galeri_kur(dim=8, seed=0):
    """İki bireyli galeri: her birinin 2 karesi var.

    t001'in kareleri birbirine yakın (aynı yöne bakan iki gözlem),
    t002 dik bir yönde — böylece karışması beklenmez.
    """
    rng = np.random.default_rng(seed)
    a = np.zeros(dim); a[0] = 1.0
    b = np.zeros(dim); b[1] = 1.0
    gurultu = lambda: rng.normal(0, 0.05, dim)  # noqa: E731
    return SahteDB([
        kayit('T001_0', 't001', a + gurultu()),
        kayit('T001_1', 't001', a + gurultu()),
        kayit('T002_0', 't002', b + gurultu()),
        kayit('T002_1', 't002', b + gurultu()),
    ])


class TestKimlikAnahtari(unittest.TestCase):

    def test_identity_alani_kullanilir(self):
        self.assertEqual(
            kimlik_anahtari({'identity': 'T001', 'turtle_id': 'T001_0'}), 't001')

    def test_identity_yoksa_kare_numarasi_atilir(self):
        """Eski galeriler `identity` taşımıyor; T001_0 ve T001_1 aynı birey."""
        self.assertEqual(kimlik_anahtari({'turtle_id': 'T001_0'}), 't001')
        self.assertEqual(kimlik_anahtari({'turtle_id': 'T001_1'}), 't001')

    def test_sayisal_olmayan_ek_korunur(self):
        """'_abc' kare numarası değil; kimliğin parçası sayılmalı."""
        self.assertEqual(kimlik_anahtari({'turtle_id': 'T001_abc'}), 't001_abc')


class TestKimlikIndeksi(unittest.TestCase):

    def test_kareler_bireyde_toplanir(self):
        idx = KimlikIndeksi(galeri_kur().get_all_turtles())
        self.assertEqual(len(idx), 2, '4 kare 2 bireye toplanmalıydı')
        self.assertEqual(idx.identities, ['t001', 't002'])
        self.assertEqual([m.shape for m in idx.matrisler], [(2, 8), (2, 8)])
        self.assertEqual(idx.kayit_sayisi, 4)

    def test_uyumsuz_boyuttaki_kayit_ayiklanir(self):
        """Kısmen yeniden gömülmüş galeri sessizce karışmamalı."""
        kayitlar = galeri_kur().get_all_turtles()
        kayitlar.append(kayit('T003_0', 't003', np.ones(4)))   # 4-d, azınlık
        idx = KimlikIndeksi(kayitlar)
        self.assertEqual(idx.dim, 8)
        self.assertEqual(idx.atlanan, 1)
        self.assertNotIn('t003', idx.identities)

    def test_bos_galeri(self):
        idx = KimlikIndeksi([])
        self.assertEqual(len(idx), 0)
        self.assertEqual(idx.dim, 0)


class TestEslestirme(unittest.TestCase):

    def setUp(self):
        self.m = TurtleMatcher(db=galeri_kur())

    def test_dogru_bireyi_bulur(self):
        sorgu = self.m.db.get_turtle_by_id('T001_0')['biometric_vector']
        r = self.m.match(sorgu)
        self.assertTrue(r.matched)
        self.assertEqual(r.matched_identity, 't001')
        self.assertEqual(r.supporting_frames, 2)

    def test_matched_turtle_id_hala_kare_kimligi(self):
        """Geriye dönük uyumluluk: mevcut istemciler 'T001_0' bekliyor.

        Yeni bilgi `matched_identity` alanında; eski alan bozulmadı.
        """
        sorgu = self.m.db.get_turtle_by_id('T001_1')['biometric_vector']
        r = self.m.match(sorgu)
        self.assertEqual(r.matched_turtle_id, 'T001_1')
        self.assertEqual(r.matched_turtle_id.rsplit('_', 1)[0].lower(), 't001')

    def test_top_n_ayri_bireyler_dondurur(self):
        """ASIL REGRESYON: liste aynı bireyin kareleriyle dolmamalı."""
        sorgu = self.m.db.get_turtle_by_id('T001_0')['biometric_vector']
        alt = self.m.match_with_top_n(sorgu, top_n=5)['top_alternatives']
        kimlikler = [a['identity'] for a in alt]
        self.assertEqual(len(kimlikler), len(set(kimlikler)),
                         'top-N aynı bireyi birden fazla kez döndürdü')
        self.assertEqual(kimlikler[0], 't001')
        self.assertEqual(alt[0]['frames'], 2)

    def test_tek_kotu_kare_bireyi_dusurmez(self):
        """A2'nin asıl faydası: centroid tek bir aykırı kareyi dengeler.

        t002'ye biri iyi biri çok kötü iki kare veriyoruz. Saf `max` iyi
        kareyi bulur; asıl risk, sorgunun kötü kareye denk gelip bireyin
        listeden düşmesi. Karışım skoru her iki kareyi de hesaba katar.
        """
        dim = 8
        hedef = np.zeros(dim); hedef[1] = 1.0
        db = SahteDB([
            kayit('T001_0', 't001', np.eye(dim)[0]),
            kayit('T001_1', 't001', np.eye(dim)[0]),
            kayit('T002_0', 't002', hedef),                 # iyi kare
            kayit('T002_1', 't002', np.eye(dim)[7]),        # alakasız kare
        ])
        m = TurtleMatcher(db=db)
        r = m.match([float(x) for x in hedef])
        self.assertEqual(r.matched_identity, 't002')

    def test_esik_altinda_yeni_birey(self):
        dik = np.zeros(8); dik[5] = 1.0
        r = self.m.match([float(x) for x in dik])
        self.assertFalse(r.matched)
        self.assertEqual(r.classification, 'NEW_INDIVIDUAL')
        self.assertIsNone(r.matched_turtle_id)

    def test_bos_galeri_cokmez(self):
        r = TurtleMatcher(db=SahteDB([])).match([0.1] * 8)
        self.assertFalse(r.matched)
        self.assertEqual(r.classification, 'NEW_INDIVIDUAL')
        self.assertEqual(r.confidence, 0.0)

    def test_boyut_uyusmazligi_cokmez(self):
        """Model değişip galeri yeniden gömülmediyse hata değil, açık sonuç."""
        r = self.m.match([0.1] * 3)
        self.assertEqual(r.classification, 'NEW_INDIVIDUAL')
        self.assertEqual(r.confidence, 0.0)

    def test_skor_araligi(self):
        for kayit_ in self.m.db.get_all_turtles():
            r = self.m.match(kayit_['biometric_vector'])
            self.assertGreaterEqual(r.confidence, 0.0)
            self.assertLessEqual(r.confidence, 1.0)

    def test_karisim_agirligi_uc_degerleri(self):
        """w=1 saf max, w=0 saf centroid; ikisi de aynı bireyi bulmalı."""
        sorgu = self.m.db.get_turtle_by_id('T001_0')['biometric_vector']
        for w in (0.0, DEFAULT_MAX_WEIGHT, 1.0):
            r = TurtleMatcher(db=galeri_kur(), max_weight=w).match(sorgu)
            self.assertEqual(r.matched_identity, 't001', f'w={w}')

    def test_max_agirligi_kirpilir(self):
        self.assertEqual(TurtleMatcher(db=galeri_kur(), max_weight=5.0).max_weight, 1.0)
        self.assertEqual(TurtleMatcher(db=galeri_kur(), max_weight=-1.0).max_weight, 0.0)

    def test_oklid_stratejisi(self):
        m = TurtleMatcher(db=galeri_kur(), strategy='euclidean')
        sorgu = m.db.get_turtle_by_id('T002_0')['biometric_vector']
        self.assertEqual(m.match(sorgu).matched_identity, 't002')

    def test_indeks_galeri_buyuyunce_tazelenir(self):
        """Kayıt eklendiğinde önbelleğe alınmış indeks bayatlamamalı."""
        self.assertEqual(len(self.m._indeks()), 2)
        yeni = np.zeros(8); yeni[3] = 1.0
        self.m.db.database['T003_0'] = kayit('T003_0', 't003', yeni)
        self.assertEqual(len(self.m._indeks()), 3)
        self.assertEqual(self.m.match([float(x) for x in yeni]).matched_identity,
                         't003')


if __name__ == '__main__':
    unittest.main(verbosity=2)
