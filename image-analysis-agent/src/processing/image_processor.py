import cv2
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Görüntü ön işleme ve işleme
    """

    def __init__(self, target_size: Tuple[int, int] = (640, 640)):
        """
        Initialize processor
        
        Args:
            target_size: Target image size for model
        """
        self.target_size = target_size

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Görüntüyü model için ön işle
        
        Args:
            image: Input image (BGR)
            
        Returns:
            Processed image
        """
        try:
            # Resize
            processed = cv2.resize(image, self.target_size)
            
            # Normalize
            processed = processed.astype(np.float32) / 255.0
            
            # Convert to RGB
            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
            
            logger.debug(f"Image preprocessed: {processed.shape}")
            return processed
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise

    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """
        Görüntü kalitesini artır
        
        Args:
            image: Input image
            
        Returns:
            Enhanced image
        """
        try:
            # CLAHE (Contrast Limited Adaptive Histogram Equalization)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            enhanced = cv2.merge((l, a, b))
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            raise

    def detect_shell(self, image: np.ndarray) -> Tuple[np.ndarray, dict]:
        """
        Karapaksı (kabuk) algıla ve izole et
        
        Args:
            image: Input image
            
        Returns:
            Cropped shell region and bounding box
        """
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define range for turtle shell (brown to dark colors)
            lower_shell = np.array([10, 50, 50])
            upper_shell = np.array([35, 200, 200])
            
            # Create mask
            mask = cv2.inRange(hsv, lower_shell, upper_shell)
            
            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # Extract region
                shell_region = image[y:y+h, x:x+w]
                
                bbox = {'x': x, 'y': y, 'width': w, 'height': h, 'area': w*h}
                
                return shell_region, bbox
            else:
                return image, {'error': 'Shell not detected'}
            
        except Exception as e:
            logger.error(f"Error detecting shell: {e}")
            return image, {'error': str(e)}

    def extract_shell_pattern(self, image: np.ndarray) -> np.ndarray:
        """
        Karapaksı deseni çıkar (özür biçimi)
        
        Args:
            image: Input image
            
        Returns:
            Pattern features
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Compute edge map using Canny
            edges = cv2.Canny(gray, 50, 150)
            
            # Compute histogram
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = cv2.normalize(hist, hist).flatten()
            
            # Compute texture features (LBP-like)
            # Placeholder for actual LBP or SIFT features
            
            return edges
            
        except Exception as e:
            logger.error(f"Error extracting pattern: {e}")
            raise

    def adjust_brightness_contrast(
        self,
        image: np.ndarray,
        brightness: float = 0,
        contrast: float = 1.0
    ) -> np.ndarray:
        """
        Parlaklık ve kontrast ayarla
        
        Args:
            image: Input image
            brightness: -100 to 100
            contrast: 0.5 to 3.0
            
        Returns:
            Adjusted image
        """
        try:
            adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
            return adjusted
            
        except Exception as e:
            logger.error(f"Error adjusting brightness/contrast: {e}")
            raise

    def denoise_image(self, image: np.ndarray) -> np.ndarray:
        """
        Gürültü azalt
        
        Args:
            image: Input image
            
        Returns:
            Denoised image
        """
        try:
            denoised = cv2.fastNlMeansDenoisingColored(
                image,
                None,
                h=10,
                hForColorComponents=10,
                templateWindowSize=7,
                searchWindowSize=21
            )
            return denoised
            
        except Exception as e:
            logger.error(f"Error denoising image: {e}")
            raise
