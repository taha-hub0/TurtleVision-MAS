"""
Gömü determinizmi regresyon testleri.

Neden var
---------
`turtle_model.py` bir zamanlar ResNet50'nin son katmanını
`nn.Linear(2048, 128)` ile değiştiriyordu. Bu katman rastgele ilkleniyor,
hiç eğitilmiyor ve diske kaydedilmiyordu — yani **her süreç başlangıcında
farklı bir projeksiyon** oluşuyordu.

Aynı fotoğraf, ajan yeniden başlatıldıktan sonra kosinüs benzerliği
**-0.1377** olan bambaşka bir vektör veriyordu. Sonuç: `kaggle_db.json`
içindeki kayıtlı vektörler her yeniden başlatmada sessizce geçersizleşiyor,
eşleştirme çalışıyor gibi görünüp anlamsız sonuç üretiyordu.

Depodaki `check_deterministic.py` bunu yakalayamaz: yalnızca *aynı süreç
içindeki* iki çağrıyı karşılaştırır ve o test her zaman geçer. Asıl testi
aşağıdaki `test_surecler_arasi_determinizm` yapıyor — modeli ayrı bir
Python sürecinde kurup sonucu karşılaştırır.

Çalıştırma:
    cd image-analysis-agent && python -m pytest tests/ -v
    (pytest yoksa: python tests/test_determinism.py)
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

import numpy as np

AGENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, AGENT_DIR)

from src.models.turtle_model import TurtleIdentificationModel

# Ayrı süreçte modeli kurup tek bir görüntünün gömüsünü yazan betik.
CHILD_SCRIPT = """
import json, sys, numpy as np, cv2
sys.path.insert(0, sys.argv[1])
from src.models.turtle_model import TurtleIdentificationModel
img = cv2.imread(sys.argv[2])
m = TurtleIdentificationModel()
f = m.extract_features(img)
json.dump([float(x) for x in f], open(sys.argv[3], 'w'))
"""


def sabit_goruntu(path):
    """Deterministik sahte görüntü — test dış veriye bağlı olmasın."""
    import cv2
    rng = np.random.default_rng(1234)
    img = (rng.random((300, 300, 3)) * 255).astype(np.uint8)
    cv2.imwrite(path, img)
    return path


class TestGomuDeterminizmi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.img_path = sabit_goruntu(os.path.join(cls.tmp.name, 'ornek.png'))
        cls.script = os.path.join(cls.tmp.name, 'child.py')
        with open(cls.script, 'w', encoding='utf-8') as f:
            f.write(CHILD_SCRIPT)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def _ayri_surecte_gomu(self, etiket):
        out = os.path.join(self.tmp.name, f'{etiket}.json')
        r = subprocess.run(
            [sys.executable, self.script, AGENT_DIR, self.img_path, out],
            capture_output=True, text=True, cwd=AGENT_DIR)
        self.assertEqual(r.returncode, 0, f'alt sürec hata verdi:\n{r.stderr[-800:]}')
        with open(out, encoding='utf-8') as f:
            return np.array(json.load(f), dtype=np.float32)

    # ---------------------------------------------------------------- #

    def test_ayni_surecte_determinizm(self):
        """check_deterministic.py'nin karşılığı — bu zaten geçiyordu."""
        import cv2
        img = cv2.imread(self.img_path)
        m = TurtleIdentificationModel()
        a, b = m.extract_features(img), m.extract_features(img)
        np.testing.assert_allclose(a, b, rtol=1e-5, atol=1e-6)

    def test_surecler_arasi_determinizm(self):
        """ASIL REGRESYON: ajan yeniden başlayınca gömü değişmemeli.

        Eğitilmemiş rastgele bir katman devreye girerse bu test düşer.
        """
        a = self._ayri_surecte_gomu('run1')
        b = self._ayri_surecte_gomu('run2')

        self.assertEqual(a.shape, b.shape, 'gömü boyutu süreçler arası değişti')

        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        self.assertGreater(na, 0)
        cos = float(np.dot(a, b) / (na * nb))
        self.assertGreater(
            cos, 0.9999,
            f'Aynı fotoğraf iki ayrı süreçte farklı gömü verdi (kosinüs={cos:.6f}). '
            'Muhtemel sebep: modelde eğitilmemiş/rastgele ilklenen bir katman var '
            've diske kaydedilmiyor.')

    def test_model_bilgisi_gercek_boyutu_bildirir(self):
        m = TurtleIdentificationModel()
        info = m.get_model_info()
        import cv2
        gercek = m.extract_features(cv2.imread(self.img_path)).shape[0]
        self.assertEqual(info['output_dimension'], gercek,
                         'get_model_info bildirilen boyut gerçek gömüyle uyuşmuyor')

    def test_gomu_l2_normalize(self):
        """Kosinüs eşiği ancak vektörler birim uzunluktaysa anlamlı."""
        import cv2
        m = TurtleIdentificationModel()
        f = m.extract_features(cv2.imread(self.img_path))
        self.assertAlmostEqual(float(np.linalg.norm(f)), 1.0, places=4)

    def test_flip_tta_varsayilan_acik(self):
        """Varsayılan açık; ortam değişkeniyle kapatılabilir olmalı."""
        self.assertTrue(TurtleIdentificationModel().flip_tta)
        self.assertFalse(TurtleIdentificationModel(flip_tta=False).flip_tta)

        onceki = os.environ.get('TURTLE_FLIP_TTA')
        try:
            os.environ['TURTLE_FLIP_TTA'] = '0'
            self.assertFalse(TurtleIdentificationModel().flip_tta)
            os.environ['TURTLE_FLIP_TTA'] = 'off'
            self.assertFalse(TurtleIdentificationModel().flip_tta)
            os.environ['TURTLE_FLIP_TTA'] = '1'
            self.assertTrue(TurtleIdentificationModel().flip_tta)
        finally:
            if onceki is None:
                os.environ.pop('TURTLE_FLIP_TTA', None)
            else:
                os.environ['TURTLE_FLIP_TTA'] = onceki

    def test_flip_tta_gomuyu_aynalamaya_duyarsiz_yapar(self):
        """A4'ün asıl kazandırdığı değişmez: f(x) == f(ayna(x)).

        TTA açıkken gömü, düz ve aynalanmış görüntünün ortalamasıdır:
            f(x)       = (g(x) + g(ayna x)) / 2
            f(ayna x)  = (g(ayna x) + g(x)) / 2
        Yani ikisi aynıdır. Kaplumbağa kareye soldan da sağdan da girebildiği
        için bu, modele gereksiz bir varyansı ortadan kaldırır.

        TTA kapalıyken bu eşitlik yoktur — testin ikinci yarısı onu doğrular
        ve böylece birinci yarının boş bir tekrar olmadığını gösterir.
        """
        import cv2
        img = cv2.imread(self.img_path)
        ayna = cv2.flip(img, 1)

        acik = TurtleIdentificationModel(flip_tta=True)
        a, b = acik.extract_features(img), acik.extract_features(ayna)
        self.assertGreater(
            float(np.dot(a, b)), 0.999,
            'flip-TTA açıkken gömü aynalamaya duyarsız olmalıydı')

        kapali = TurtleIdentificationModel(flip_tta=False)
        c, d = kapali.extract_features(img), kapali.extract_features(ayna)
        self.assertLess(
            float(np.dot(c, d)), 0.999,
            'TTA kapalıyken aynalama gömüyü değiştirmeliydi; test anlamsız')

    def test_flip_tta_gomuyu_degistirir(self):
        """Bayrak gerçekten farklı bir gömü üretiyor mu?

        Üretiyorsa galeri ve sorgu AYNI ayarla üretilmek zorundadır; bu
        yüzden `build_gallery.py` ayarı kaggle_db.meta.json'a yazıyor ve
        `app.py` açılışta doğruluyor.
        """
        import cv2
        img = cv2.imread(self.img_path)
        a = TurtleIdentificationModel(flip_tta=True).extract_features(img)
        b = TurtleIdentificationModel(flip_tta=False).extract_features(img)
        self.assertLess(float(np.dot(a, b)), 0.9999)

    def test_flip_tta_deterministik(self):
        """İki ileri geçişin ortalaması da süreç içinde kararlı olmalı."""
        import cv2
        img = cv2.imread(self.img_path)
        m = TurtleIdentificationModel(flip_tta=True)
        np.testing.assert_allclose(m.extract_features(img),
                                   m.extract_features(img),
                                   rtol=1e-5, atol=1e-6)

    def test_model_bilgisi_flip_tta_bildirir(self):
        self.assertIs(TurtleIdentificationModel().get_model_info()['flip_tta'],
                      True)

    def test_farkli_goruntu_farkli_gomu(self):
        """Model girdiye gerçekten bakıyor mu (sabit çıktı vermiyor mu)?"""
        import cv2
        ikinci = os.path.join(self.tmp.name, 'ornek2.png')
        rng = np.random.default_rng(999)
        cv2.imwrite(ikinci, (rng.random((300, 300, 3)) * 255).astype(np.uint8))

        m = TurtleIdentificationModel()
        a = m.extract_features(cv2.imread(self.img_path))
        b = m.extract_features(cv2.imread(ikinci))
        self.assertLess(float(np.dot(a, b)), 0.999,
                        'iki farklı görüntü aynı gömüyü verdi')


if __name__ == '__main__':
    unittest.main(verbosity=2)
