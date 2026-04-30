import os
from dotenv import load_dotenv

load_dotenv()

# Server Configuration
PORT = int(os.getenv('PORT', 5001))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# SQLite Configuration
DB_PATH = os.getenv('DB_PATH', './turtle_id.db')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', './logs/database_agent.log')

# Coordinator Communication
COORDINATOR_URL = os.getenv('COORDINATOR_URL', 'http://localhost:3000')

# Image Analysis Agent
IMAGE_AGENT_URL = os.getenv('IMAGE_AGENT_URL', 'http://localhost:5000')
