#!/bin/bash
# Turtle-ID Multi-Agent System - Development Setup

set -e

echo "╔═══════════════════════════════════════════════════════╗"
echo "║  Turtle-ID - Development Environment Setup            ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Check Node.js
echo "Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi
echo "✓ Node.js $(node --version)"

# Check Python
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.9+"
    exit 1
fi
echo "✓ Python $(python3 --version)"

# Check MySQL
echo "Checking MySQL..."
if ! command -v mysql &> /dev/null; then
    echo "⚠ MySQL not found. Please install MySQL 8.0+"
    echo "  You can also use Docker: docker run -d -p 3306:3306 mysql:8.0"
fi

# Setup Backend
echo ""
echo "📦 Setting up Backend..."
cd backend
npm install
cp .env.example .env
echo "✓ Backend setup complete"

# Setup Image Analysis Agent
echo ""
echo "📦 Setting up Image Analysis Agent..."
cd ../image-analysis-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
echo "✓ Image Analysis Agent setup complete"

# Setup Database Agent
echo ""
echo "📦 Setting up Database Agent..."
cd ../database-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
echo "✓ Database Agent setup complete"

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║  Setup Complete! 🎉                                   ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Configure environment variables in .env files"
echo "  2. Set up MySQL database (if not using Docker)"
echo "  3. Run database migrations:"
echo "     cd database-agent && python migrate.py"
echo "  4. Start services in separate terminals:"
echo "     Terminal 1: cd backend && npm run dev"
echo "     Terminal 2: cd image-analysis-agent && source venv/bin/activate && python app.py"
echo "     Terminal 3: cd database-agent && source venv/bin/activate && python app.py"
echo ""
echo "Or use Docker:"
echo "  docker-compose up -d"
echo ""
