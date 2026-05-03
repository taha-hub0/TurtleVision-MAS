from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
import cv2
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
import logging
from flask import send_from_directory

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

        if analysis_result.get('confidence', 1.0) < CONFIDENCE_THRESHOLD:
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


# ============================================================================
# SeaTurtleID2022 Matching Endpoints
# ============================================================================
# Matching Agent tarafından çağrılır. Gelen biyometrik vektörü
# veritabanıyla karşılaştırır ve %60 eşikle sınıflandırır.

try:
    from src.matching.turtle_matcher import TurtleMatcher
    matcher = TurtleMatcher(threshold=0.60, method='cosine')
    logger.info("Turtle Matcher initialized successfully (SeaTurtleID2022)")
except Exception as e:
    logger.warning(f"Turtle Matcher not available: {e}")
    matcher = None


@app.route('/api/match', methods=['POST'])
def match_turtle():
    """
    Biyometrik vektörü veritabanıyla eşleştir.
    
    Request JSON:
    {
        "biometric_vector": [0.45, 0.23, ..., 0.78],  # 128 eleman
        "threshold": 0.60,  # Optional
        "method": "cosine",  # Optional: 'cosine' | 'euclidean'
        "metadata": {...}  # Optional: fotoğraf metadatası
    }
    """
    request_id = request.headers.get('X-Request-ID', 'unknown')
    
    try:
        if matcher is None:
            return jsonify({
                'success': False,
                'error': 'Matcher not initialized',
                'request_id': request_id
            }), 503

        data = request.get_json()
        
        if not data or 'biometric_vector' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing biometric_vector',
                'request_id': request_id
            }), 400

        biometric_vector = data.get('biometric_vector')
        
        if not isinstance(biometric_vector, list) or len(biometric_vector) != 128:
            return jsonify({
                'success': False,
                'error': 'biometric_vector must be a list of 128 numbers',
                'request_id': request_id
            }), 400

        # Eşleştirme yap
        logger.info(f"[{request_id}] Matching turtle biometric vector...")
        match_result = matcher.match(biometric_vector)
        
        logger.info(
            f"[{request_id}] Match result: {match_result.classification} "
            f"(confidence: {match_result.confidence*100:.1f}%)"
        )

        return jsonify({
            'success': True,
            'request_id': request_id,
            'matched': match_result.matched,
            'classification': match_result.classification,
            'confidence': match_result.confidence,
            'matched_turtle_id': match_result.matched_turtle_id,
            'similarity_score': match_result.similarity_score,
            'matching_method': match_result.matching_method,
            'reasoning': match_result.reasoning,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"[{request_id}] Matching error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'request_id': request_id
        }), 500


@app.route('/api/register', methods=['POST'])
def register_turtle():
    """Yeni bir kaplumbağayı veritabanına ekle"""
    request_id = request.headers.get('X-Request-ID', 'unknown')
    try:
        data = request.get_json()
        biometric_vector = data.get('biometric_vector')
        turtle_id = data.get('turtle_id', f"TURTLE_{datetime.now().strftime('%H%M%S')}")
        
        if not biometric_vector or len(biometric_vector) != 128:
            return jsonify({'success': False, 'error': 'Invalid biometric vector'}), 400
            
        record = {
            'turtle_id': turtle_id,
            'species': 'GREEN_TURTLE',
            'biometric_vector': biometric_vector,
            'location': data.get('location', 'Bilinmeyen Konum'),
            'first_recorded': datetime.now().isoformat(),
            'sightings': 1,
            'quality_score': 0.99
        }
        
        # Fiziksel resmi kaydet
        image_base64 = data.get('image')
        if image_base64:
            gallery_dir = os.path.join(os.path.dirname(__file__), 'data', 'gallery')
            os.makedirs(gallery_dir, exist_ok=True)
            try:
                img_data = base64.b64decode(image_base64)
                with open(os.path.join(gallery_dir, f"{turtle_id}.jpg"), "wb") as f:
                    f.write(img_data)
            except Exception as e:
                logger.error(f"Görsel kaydedilemedi: {e}")
        
        if hasattr(matcher.db, 'add_turtle'):
            matcher.db.add_turtle(turtle_id, record)
        
        return jsonify({
            'success': True,
            'turtle_id': turtle_id,
            'message': 'Successfully registered to database'
        }), 200
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/gallery', methods=['GET'])
def get_gallery():
    """Galeriye kaydedilen resimlerin listesini döndür"""
    gallery_dir = os.path.join(os.path.dirname(__file__), 'data', 'gallery')
    os.makedirs(gallery_dir, exist_ok=True)
    
    db_records = getattr(matcher.db, 'database', {})
    
    images = []
    for filename in os.listdir(gallery_dir):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            t_id = filename.split('.')[0]
            record = db_records.get(t_id, {})
            location = record.get('location', 'Bilinmeyen Konum')
            
            images.append({
                'id': t_id,
                'url': f"http://localhost:5000/api/gallery/{filename}",
                'location': location
            })
    
    return jsonify({'success': True, 'images': images})

@app.route('/api/gallery/<filename>', methods=['GET'])
def serve_gallery_image(filename):
    """Galerideki fiziksel bir resmi sunar"""
    gallery_dir = os.path.join(os.path.dirname(__file__), 'data', 'gallery')
    return send_from_directory(gallery_dir, filename)

@app.route('/api/gallery/<turtle_id>', methods=['DELETE'])
def delete_gallery_image(turtle_id):
    """Galeriden resmi ve veritabanı kaydını sil"""
    try:
        # 1. Dosyayı sil
        gallery_dir = os.path.join(os.path.dirname(__file__), 'data', 'gallery')
        filepath = os.path.join(gallery_dir, f"{turtle_id}.jpg")
        if os.path.exists(filepath):
            os.remove(filepath)
            
        # 2. Veritabanından kaydı sil
        if hasattr(matcher.db, 'delete_turtle'):
            matcher.db.delete_turtle(turtle_id)
            
        return jsonify({'success': True, 'message': 'Başarıyla silindi'})
    except Exception as e:
        logger.error(f"Silme hatası: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/match-top-n', methods=['POST'])
def match_turtle_top_n():
    """
    En benzer N kayıtla birlikte eşleştirme sonucu döndür.
    (İnsan müdahalesi gereken durumlar için)
    
    Request JSON:
    {
        "biometric_vector": [0.45, 0.23, ..., 0.78],
        "top_n": 5,  # Optional, default 5
        "threshold": 0.60,  # Optional
        "method": "cosine"  # Optional
    }
    """
    request_id = request.headers.get('X-Request-ID', 'unknown')
    
    try:
        if matcher is None:
            return jsonify({
                'success': False,
                'error': 'Matcher not initialized'
            }), 503

        data = request.get_json()
        
        if not data or 'biometric_vector' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing biometric_vector'
            }), 400

        biometric_vector = data.get('biometric_vector')
        top_n = data.get('top_n', 5)
        
        if not isinstance(biometric_vector, list) or len(biometric_vector) != 128:
            return jsonify({
                'success': False,
                'error': 'biometric_vector must be a list of 128 numbers'
            }), 400

        # Top N eşleştirme
        logger.info(f"[{request_id}] Matching top {top_n} alternatives...")
        result = matcher.match_with_top_n(biometric_vector, top_n=top_n)
        
        main_result = result['main_result']
        logger.info(f"[{request_id}] Top-N match completed")

        return jsonify({
            'success': True,
            'request_id': request_id,
            'main_result': {
                'matched': main_result.matched,
                'classification': main_result.classification,
                'confidence': main_result.confidence,
                'matched_turtle_id': main_result.matched_turtle_id,
                'similarity_score': main_result.similarity_score,
                'reasoning': main_result.reasoning,
            },
            'top_alternatives': [
                {
                    'turtle_id': alt['turtle_id'],
                    'species': alt['species'],
                    'similarity': alt['similarity'],
                }
                for alt in result['top_alternatives']
            ],
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"[{request_id}] Top-N matching error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
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
