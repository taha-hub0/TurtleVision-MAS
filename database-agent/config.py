import os
from dotenv import load_dotenv

load_dotenv()

# Server Configuration
PORT = int(os.getenv('PORT', 5001))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Database Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'turtle_id_db')

# Connection Pool
DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 10))
DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', 20))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', './logs/database_agent.log')

# Coordinator Communication
COORDINATOR_URL = os.getenv('COORDINATOR_URL', 'http://localhost:3000')

# Image Analysis Agent
IMAGE_AGENT_URL = os.getenv('IMAGE_AGENT_URL', 'http://localhost:5000')
