from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
import cv2
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
import logging

from src.models.turtle_model import TurtleIdentificationModel
from src.processing.image_processor import ImageProcessor
from src.agents.biolytics import BiolyticsAgent

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
PORT = int(os.getenv('PORT', 5000))
MODEL_PATH = os.getenv('MODEL_PATH', './src/models/weights/best_model.pt')
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.85))

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize model and processor
try:
    model = TurtleIdentificationModel(MODEL_PATH)
    processor = ImageProcessor()
    biolytics = BiolyticsAgent()
    logger.info("Model loaded successfully")
    logger.info("Biolytics Agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None
    processor = None
    biolytics = None


@app.route('/health', methods=['GET'])
def health_check():
    """Sağlık kontrolü"""
    return jsonify({
        'status': 'healthy',
        'service': 'image-analysis-agent',
        'model_loaded': model is not None,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """
    Görüntü analiz yapma
    Expected JSON:
    {
        "image": "base64_encoded_image",
        "metadata": {
            "location": "beach_name",
            "date": "YYYY-MM-DD",
            "observer": "name"
        }
    }
    """
    request_id = request.headers.get('X-Request-ID', 'unknown')
    
    try:
        if model is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded',
                'request_id': request_id
            }), 503

        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing image data',
                'request_id': request_id
            }), 400

        image_base64 = data['image']
        metadata = data.get('metadata', {})

        # Decode image
        logger.info(f"[{request_id}] Decoding image...")
        image_data = base64.b64decode(image_base64)
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({
                'success': False,
                'error': 'Invalid image format',
                'request_id': request_id
            }), 400

        # Process image
        logger.info(f"[{request_id}] Processing image...")
        processed_image = processor.preprocess(image)

        # Analyze image
        logger.info(f"[{request_id}] Analyzing image with model...")
        analysis_result = model.identify_turtle(processed_image)

        if analysis_result['confidence'] < CONFIDENCE_THRESHOLD:
            analysis_result['warning'] = 'Low confidence match'

        # Extract features for similarity search
        features = model.extract_features(processed_image)

        response = {
            'success': True,
            'request_id': request_id,
            'analysis': analysis_result,
            'features': features.tolist() if isinstance(features, np.ndarray) else features,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }

        logger.info(f"[{request_id}] Analysis completed successfully")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"[{request_id}] Error during analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'request_id': request_id
        }), 500


@app.route('/api/features', methods=['POST'])
def extract_features():
    """
    Görüntü özelliklerini çıkar
    """
    request_id = request.headers.get('X-Request-ID', 'unknown')

    try:
        if model is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded'
            }), 503

        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing image data'
            }), 400

        image_base64 = data['image']

        # Decode image
        image_data = base64.b64decode(image_base64)
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({
                'success': False,
                'error': 'Invalid image format'
            }), 400

        # Process image
        processed_image = processor.preprocess(image)

        # Extract features
        features = model.extract_features(processed_image)

        return jsonify({
            'success': True,
            'request_id': request_id,
            'features': features.tolist() if isinstance(features, np.ndarray) else features,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error extracting features: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/model/info', methods=['GET'])
def model_info():
    """Model bilgisi"""
    return jsonify({
        'service': 'image-analysis-agent',
        'model_path': MODEL_PATH,
        'confidence_threshold': CONFIDENCE_THRESHOLD,
        'status': 'loaded' if model is not None else 'not_loaded',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/biolytics/health', methods=['GET'])
def biolytics_health():
    """Biolytics Agent sağlık kontrolü"""
    if biolytics is None:
        return jsonify({
            'status': 'unhealthy',
            'error': 'Biolytics agent not initialized'
        }), 503
    
    health = biolytics.health()
    return jsonify(health), 200


@app.route('/api/biolytics/analyze', methods=['POST'])
def biolytics_analyze():
    """
    Biolytics Agent: Strateji seçerek görüntüyü analiz et
    """
    request_id = request.headers.get('X-Request-ID', 'unknown')
    
    try:
        if biolytics is None:
            return jsonify({
                'success': False,
                'error': 'Biolytics agent not initialized'
            }), 503

        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing image data'
            }), 400

        image_base64 = data['image']
        strategy = data.get('strategy', None)

        # Decode image
        image_data = base64.b64decode(image_base64)
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({
                'success': False,
                'error': 'Invalid image format'
            }), 400

        # Biolytics analizi yap
        logger.info(f"[{request_id}] Analyzing with strategy: {strategy}")
        analysis_result = biolytics.analyze_image(image, strategy)

        return jsonify({
            'success': analysis_result.get('success', True),
            'request_id': request_id,
            'analysis': analysis_result,
            'timestamp': datetime.now().isoformat()
        }), 200 if analysis_result.get('success') else 400

    except Exception as e:
        logger.error(f"[{request_id}] Biolytics analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'request_id': request_id
        }), 500


@app.route('/api/biolytics/auto-detect', methods=['POST'])
def biolytics_auto_detect():
    """
    Biolytics Agent: Otomatik tür bulma
    Tüm stratejileri dene ve en iyi eşleşmeyi dön
    """
    request_id = request.headers.get('X-Request-ID', 'unknown')
    
    try:
        if biolytics is None:
            return jsonify({
                'success': False,
                'error': 'Biolytics agent not initialized'
            }), 503

        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing image data'
            }), 400

        image_base64 = data['image']

        # Decode image
        image_data = base64.b64decode(image_base64)
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({
                'success': False,
                'error': 'Invalid image format'
            }), 400

        # Auto-detect yap
        logger.info(f"[{request_id}] Auto-detecting turtle species")
        detection_result = biolytics.auto_detect_species(image)

        return jsonify({
            'success': detection_result.get('success', True),
            'request_id': request_id,
            'detection': detection_result,
            'timestamp': datetime.now().isoformat()
        }), 200 if detection_result.get('success') else 400

    except Exception as e:
        logger.error(f"[{request_id}] Auto-detect error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'request_id': request_id
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'path': request.path
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500


if __name__ == '__main__':
    logger.info(f"Starting Image Analysis Agent on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=False)
