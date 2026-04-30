import os
from dotenv import load_dotenv

load_dotenv()

# Server Configuration
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Model Configuration
MODEL_PATH = os.getenv('MODEL_PATH', './src/models/weights/best_model.pt')
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.85))
MODEL_INPUT_SIZE = (640, 640, 3)

# Image Processing
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FORMATS = ['jpg', 'jpeg', 'png', 'bmp', 'tiff']

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', './logs/image_analysis_agent.log')

# Coordinator Communication
COORDINATOR_URL = os.getenv('COORDINATOR_URL', 'http://localhost:3000')

# Database Agent
DB_AGENT_URL = os.getenv('DB_AGENT_URL', 'http://localhost:5001')

# Cache Configuration
ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'True').lower() == 'true'
CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))  # 1 hour
