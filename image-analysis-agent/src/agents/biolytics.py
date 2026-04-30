/**
 * Biolytics Agent - Görüntü Analiz Ajanı
 * Strategy Pattern ile Tür Tanımlama
 * 
 * Sorumluluğu: Deniz kaplumbağalarını fotoğraflarından tanımla
 * - Yeşil Kaplumbağa (Green Turtle): Post-ocular scutes analizi
 * - Deri Sırtlı (Leatherback): Pineal spot analizi
 * - Andere türler için genişletilebilir
 * 
 * SOLID Prensipleri:
 * - S: Her strateji tek sorumluluğa sahip
 * - O: Yeni türler eklenebilir (Open/Closed)
 * - L: Tüm stratejiler interface'i implement eder
 * - I: İnce arayüzler (Interface Segregation)
 * - D: Soyut stratejilere bağımlılık
 */

from abc import ABC, abstractmethod
import cv2
import numpy as np
from typing import Dict, Tuple, List
import logging

logger = logging.getLogger(__name__)


class TurtleIdentificationStrategy(ABC):
    """
    Turt Tanımlama Stratejileri için Abstract Base Class (SOLID - Interface Segregation)
    """

    @abstractmethod
    def identify(self, image: np.ndarray) -> Dict:
        """Kaplumbağayı tanımla"""
        pass

    @abstractmethod
    def extract_biometric_code(self, image: np.ndarray) -> str:
        """Biyometrik kodu çıkar"""
        pass

    @abstractmethod
    def get_distinctive_features(self, image: np.ndarray) -> Dict:
        """Tür spesifik özellikleri çıkar"""
        pass


class GreenTurtleStrategy(TurtleIdentificationStrategy):
    """
    Yeşil Kaplumbağa Tanımlama Stratejisi
    Post-ocular Scutes (Göz Arkasındaki Pul Dizilimi) Analizi
    """

    def __init__(self):
        self.species = 'Chelonia mydas'
        self.name = 'GREEN_TURTLE'

    def identify(self, image: np.ndarray) -> Dict:
        """Yeşil kaplumbağayı tanımla"""
        try:
            # Göz arkasındaki pul dizilimini tespit et
            features = self.get_distinctive_features(image)

            # Biyometrik kodu oluştur
            biometric_code = self.extract_biometric_code(image)

            return {
                'success': True,
                'species': self.species,
                'turtle_type': self.name,
                'confidence': features.get('confidence', 0.85),
                'features': features,
                'biometric_code': biometric_code,
                'extraction_method': 'post_ocular_scutes_pattern',
            }
        except Exception as e:
            logger.error(f'Green turtle identification failed: {e}')
            return {
                'success': False,
                'error': str(e),
            }

    def extract_biometric_code(self, image: np.ndarray) -> str:
        """
        Post-ocular Scutes'den sayısal kod çıkar
        Yöntem: Her pul diziliminin şekli ve boyutu sayısal değere dönüştürülür
        """
        try:
            # Görüntüyü gri skalaya dönüştür
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Kenar tespiti (Canny)
            edges = cv2.Canny(gray, 50, 150)

            # Konturları bul
            contours, _ = cv2.findContours(
                edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
            )

            # Pul dizilimini tespit et (büyük konturlar)
            scute_patterns = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Minimum alan
                    (x, y), (w, h) = cv2.minAreaRect(contour)[0:2]
                    scute_patterns.append({
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'area': area,
                    })

            # Sayısal kod oluştur
            if scute_patterns:
                code_parts = []
                for pattern in sorted(scute_patterns, key=lambda p: p['x']):
                    # Her pul için: genişlik/yükseklik oranı hash'le
                    ratio = pattern['width'] / max(pattern['height'], 1)
                    code_parts.append(str(int(ratio * 10)))

                biometric_code = ''.join(code_parts[:20])  # İlk 20 pul
            else:
                biometric_code = '0' * 20

            return biometric_code

        except Exception as e:
            logger.error(f'Error extracting biometric code: {e}')
            return '0' * 20

    def get_distinctive_features(self, image: np.ndarray) -> Dict:
        """Yeşil kaplumbağaya ait özellikleri çıkar"""
        try:
            features = {
                'shell_color': self._detect_shell_color(image),
                'post_ocular_scutes': self._count_scutes(image),
                'head_shape': 'rounded',
                'confidence': 0.92,
            }
            return features
        except Exception as e:
            logger.error(f'Error extracting features: {e}')
            return {'error': str(e), 'confidence': 0}

    def _detect_shell_color(self, image: np.ndarray) -> str:
        """Karapaksı rengini tespit et"""
        # HSV'ye dönüştür
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Yeşil rengi ara (H: 40-80)
        lower_green = np.array([35, 50, 50])
        upper_green = np.array([85, 255, 255])

        mask = cv2.inRange(hsv, lower_green, upper_green)
        green_pixels = cv2.countNonZero(mask)

        if green_pixels > 1000:
            return 'dark_green'
        elif green_pixels > 500:
            return 'green'
        else:
            return 'brown_green'

    def _count_scutes(self, image: np.ndarray) -> int:
        """Pul sayısını hesapla"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(
            edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        return len([c for c in contours if cv2.contourArea(c) > 100])


class LeatherbackStrategy(TurtleIdentificationStrategy):
    """
    Deri Sırtlı Kaplumbağa Tanımlama Stratejisi
    Pineal Spot (Başın Üstündeki Pembe Leke) Analizi
    """

    def __init__(self):
        self.species = 'Dermochelys coriacea'
        self.name = 'LEATHERBACK'

    def identify(self, image: np.ndarray) -> Dict:
        """Deri sırtlı kaplumbağayı tanımla"""
        try:
            # Pineal spot'ı tespit et
            features = self.get_distinctive_features(image)

            # Biyometrik kodu oluştur
            biometric_code = self.extract_biometric_code(image)

            return {
                'success': True,
                'species': self.species,
                'turtle_type': self.name,
                'confidence': features.get('confidence', 0.88),
                'features': features,
                'biometric_code': biometric_code,
                'extraction_method': 'pineal_spot_analysis',
            }
        except Exception as e:
            logger.error(f'Leatherback identification failed: {e}')
            return {
                'success': False,
                'error': str(e),
            }

    def extract_biometric_code(self, image: np.ndarray) -> str:
        """
        Pineal Spot'tan sayısal kod çıkar
        Yöntem: Loke konumu, boyutu ve renk değerleri kodlanır
        """
        try:
            # Pineal spot'ı tespit et (pembe renk)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # Pembe rengi ara (H: 300-330)
            lower_pink = np.array([140, 50, 50])
            upper_pink = np.array([170, 255, 255])

            mask = cv2.inRange(hsv, lower_pink, upper_pink)
            contours, _ = cv2.findContours(
                mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
            )

            if contours:
                largest = max(contours, key=cv2.contourArea)
                M = cv2.moments(largest)
                if M['m00'] > 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    area = cv2.contourArea(largest)

                    # Kod: merkez koordinatları + alan
                    code = f'{cx:04d}{cy:04d}{int(area):06d}'
                    return code

            return '0' * 14

        except Exception as e:
            logger.error(f'Error extracting biometric code: {e}')
            return '0' * 14

    def get_distinctive_features(self, image: np.ndarray) -> Dict:
        """Deri sırtlı kaplumbağaya ait özellikleri çıkar"""
        try:
            features = {
                'pineal_spot': self._detect_pineal_spot(image),
                'shell_texture': 'leathery',
                'shell_color': 'dark_brown',
                'confidence': 0.90,
            }
            return features
        except Exception as e:
            logger.error(f'Error extracting features: {e}')
            return {'error': str(e), 'confidence': 0}

    def _detect_pineal_spot(self, image: np.ndarray) -> Dict:
        """Pineal spot'ı tespit et"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_pink = np.array([140, 50, 50])
        upper_pink = np.array([170, 255, 255])

        mask = cv2.inRange(hsv, lower_pink, upper_pink)
        pink_pixels = cv2.countNonZero(mask)

        if pink_pixels > 500:
            return {
                'detected': True,
                'size': 'large',
                'color_intensity': 'high',
            }
        elif pink_pixels > 100:
            return {
                'detected': True,
                'size': 'small',
                'color_intensity': 'medium',
            }
        else:
            return {
                'detected': False,
                'size': 'none',
                'color_intensity': 'low',
            }


class BiolyticsAgent:
    """
    Biolytics Agent - Strategy Pattern ile Tür Tanımlama
    Sorumluluğu: Uygun stratejiyı seç ve analiz yap
    """

    def __init__(self):
        self.name = 'BiolyticsAgent'
        self.version = '1.0.0'

        # Stratejileri kayıt et
        self.strategies = {
            'green': GreenTurtleStrategy(),
            'leatherback': LeatherbackStrategy(),
        }

        self.default_strategy = 'green'

    def analyze_image(self, image: np.ndarray, strategy: str = None) -> Dict:
        """
        Görüntüyü analiz et
        Strategy Pattern: Uygun stratejiyi dinamik olarak seç
        """
        try:
            # Strateji seç
            strategy_name = strategy or self.default_strategy
            strategy = self.strategies.get(strategy_name)

            if not strategy:
                return {
                    'success': False,
                    'error': f'Unknown strategy: {strategy_name}',
                }

            # Tanımlama yap
            result = strategy.identify(image)

            return result

        except Exception as e:
            logger.error(f'Analysis failed: {e}')
            return {
                'success': False,
                'error': str(e),
            }

    def auto_detect_species(self, image: np.ndarray) -> Dict:
        """
        Otomatik olarak tür belirle
        Tüm stratejileri dene ve en yüksek confidence'ı dön
        """
        results = []

        for strategy_name, strategy in self.strategies.items():
            try:
                result = strategy.identify(image)
                if result.get('success'):
                    results.append(
                        {
                            'strategy': strategy_name,
                            'confidence': result.get('confidence', 0),
                            'result': result,
                        }
                    )
            except Exception as e:
                logger.warning(f'Strategy {strategy_name} failed: {e}')

        if results:
            # En yüksek confidence'ı seç
            best = max(results, key=lambda x: x['confidence'])
            return {
                'success': True,
                'selected_strategy': best['strategy'],
                'analysis': best['result'],
                'alternatives': [
                    {
                        'strategy': r['strategy'],
                        'confidence': r['confidence'],
                    }
                    for r in results[1:]
                ],
            }
        else:
            return {
                'success': False,
                'error': 'No successful strategies',
            }

    def health(self) -> Dict:
        """Agent sağlık kontrolü"""
        return {
            'agent': self.name,
            'version': self.version,
            'status': 'healthy',
            'strategies': list(self.strategies.keys()),
            'timestamp': str(np.datetime64('now')),
        }
