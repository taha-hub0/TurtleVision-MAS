#!/bin/bash
# Turtle-ID Multi-Agent System - Quick Start Script

echo "╔═══════════════════════════════════════════════════════╗"
echo "║  Turtle-ID Multi-Agent System - Quick Start           ║"
echo "╚═══════════════════════════════════════════════════════╝"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✓ Docker found"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker Compose found"

# Start services
echo ""
echo "Starting Turtle-ID services..."
echo ""

docker-compose up -d

echo ""
echo "✓ Services started!"
echo ""
echo "Endpoints:"
echo "  - Coordinator:       http://localhost:3000"
echo "  - Image Analysis:    http://localhost:5000"
echo "  - Database Agent:    http://localhost:5001"
echo "  - MySQL:             localhost:3306"
echo ""
echo "Check health status:"
echo "  curl http://localhost:3000/api/health"
echo ""
echo "View logs:"
echo "  docker-compose logs -f"
echo ""
echo "Stop services:"
echo "  docker-compose down"
echo ""
