from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from src.database import Database
from src.models.turtle import TurtleModel
from config import DB_PATH

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
PORT = int(os.getenv('PORT', 5001))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Initialize logger
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize database
try:
    db = Database(DB_PATH)
    db.connect()
    db.create_tables()
    logger.info("Database connected successfully")
except Exception as e:
    logger.error(f"Failed to connect to database: {e}")
    db = None


@app.route('/health', methods=['GET'])
def health_check():
    """Sağlık kontrolü"""
    return jsonify({
        'status': 'healthy',
        'service': 'database-agent',
        'database': 'connected',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/turtle', methods=['POST'])
def create_turtle():
    """Yeni kaplumbağa kaydı oluştur"""
    try:
        if not db:
            return jsonify({'error': 'Database not available'}), 503

        data = request.get_json()

        # Validate required fields
        required_fields = ['id', 'imageBase64', 'analysisResult', 'metadata']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': f'Missing required fields: {required_fields}'
            }), 400

        # Create turtle record
        turtle = TurtleModel(
            id=data['id'],
            image_base64=data['imageBase64'],
            analysis_result=str(data['analysisResult']),
            metadata=str(data.get('metadata', {})),
            species=data.get('species'),
            location=data.get('location'),
            registered_at=datetime.now()
        )

        result = turtle.save(db)

        if result:
            return jsonify({
                'success': True,
                'id': turtle.id,
                'message': 'Turtle registered successfully'
            }), 201
        else:
            return jsonify({
                'error': 'Failed to save turtle'
            }), 500

    except Exception as e:
        logger.error(f"Error creating turtle: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/turtle/<turtle_id>', methods=['GET'])
def get_turtle(turtle_id):
    """Kaplumbağa bilgisi getir"""
    try:
        if not db:
            return jsonify({'error': 'Database not available'}), 503

        turtle = TurtleModel.get_by_id(db, turtle_id)

        if turtle:
            return jsonify({
                'success': True,
                'turtle': turtle.to_dict()
            }), 200
        else:
            return jsonify({
                'error': 'Turtle not found'
            }), 404

    except Exception as e:
        logger.error(f"Error fetching turtle: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/turtles', methods=['GET'])
def get_turtles():
    """Tüm kaplumbağaları getir (filtreleme seçeneği ile)"""
    try:
        if not db:
            return jsonify({'error': 'Database not available'}), 503

        # Query parameters
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        location = request.args.get('location')
        species = request.args.get('species')

        # Build query
        query = "SELECT * FROM turtles WHERE 1=1"
        params = []

        if location:
            query += " AND location = %s"
            params.append(location)

        if species:
            query += " AND species = %s"
            params.append(species)

        query += f" LIMIT {limit} OFFSET {offset}"

        results = db.execute(query, params, fetch_all=True)

        turtles = [TurtleModel.from_row(row).to_dict() for row in results]

        return jsonify({
            'success': True,
            'count': len(turtles),
            'turtles': turtles
        }), 200

    except Exception as e:
        logger.error(f"Error fetching turtles: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/turtle/<turtle_id>', methods=['PUT'])
def update_turtle(turtle_id):
    """Kaplumbağa bilgisini güncelle"""
    try:
        if not db:
            return jsonify({'error': 'Database not available'}), 503

        data = request.get_json()

        turtle = TurtleModel.get_by_id(db, turtle_id)
        if not turtle:
            return jsonify({'error': 'Turtle not found'}), 404

        # Update fields
        if 'metadata' in data:
            turtle.metadata = str(data['metadata'])
        if 'species' in data:
            turtle.species = data['species']
        if 'location' in data:
            turtle.location = data['location']

        result = turtle.update(db)

        if result:
            return jsonify({
                'success': True,
                'message': 'Turtle updated successfully',
                'turtle': turtle.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Failed to update turtle'}), 500

    except Exception as e:
        logger.error(f"Error updating turtle: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/turtle/save', methods=['POST'])
def save_turtle():
    """Kaplumbağa kaydet"""
    return create_turtle()


@app.route('/api/turtle/similarity-search', methods=['POST'])
def similarity_search():
    """
    Benzer kaplumbağaları ara
    """
    try:
        if not db:
            return jsonify({'error': 'Database not available'}), 503

        data = request.get_json()

        if 'imageFeatures' not in data:
            return jsonify({'error': 'Missing imageFeatures'}), 400

        threshold = data.get('threshold', 0.85)

        # SQL query for similarity search (simplified)
        # Gerçek implementasyonda vector similarity search kullanılacak
        query = """
        SELECT * FROM turtles 
        LIMIT 10
        """

        results = db.execute(query, fetch_all=True)
        turtles = [TurtleModel.from_row(row).to_dict() for row in results]

        return jsonify({
            'success': True,
            'matches': turtles,
            'threshold': threshold
        }), 200

    except Exception as e:
        logger.error(f"Error in similarity search: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/turtle/biometrics', methods=['GET'])
def get_biometrics():
    """
    Tüm kaplumbağaların biyometrik kodlarını getir (Matching Agent için)
    """
    try:
        if not db:
            return jsonify({'error': 'Database not available'}), 503

        # Biyometrik kodları getir
        query = """
        SELECT 
            id as turtle_id,
            species,
            analysis_result,
            registered_at
        FROM turtles
        WHERE analysis_result IS NOT NULL
        """

        results = db.execute(query, fetch_all=True)

        if not results:
            return jsonify({
                'success': True,
                'biometrics': [],
                'count': 0
            }), 200

        # Results'ı format et
        biometrics = []
        for row in results:
            try:
                # JSON'dan biometric_code'u çıkar
                import json
                analysis = json.loads(row.get('analysis_result', '{}'))
                
                biometrics.append({
                    'turtle_id': row.get('turtle_id'),
                    'species': row.get('species'),
                    'biometric_code': analysis.get('biometric_code', ''),
                    'extraction_method': analysis.get('extraction_method', ''),
                    'registered_at': row.get('registered_at'),
                    'sightings_count': 1  # Placeholder
                })
            except Exception as e:
                logger.warning(f"Error parsing biometrics for {row.get('turtle_id')}: {e}")

        return jsonify({
            'success': True,
            'biometrics': biometrics,
            'count': len(biometrics)
        }), 200

    except Exception as e:
        logger.error(f"Error fetching biometrics: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info(f"Starting Database Agent on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=False)
