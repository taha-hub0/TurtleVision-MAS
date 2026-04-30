#!/bin/bash

# Turtle-ID MAS - System Health Check Script
# 
# Bu betik tüm ajanların sağlık durumunu kontrol eder
# ve sistem test'ini çalıştırır.
#
# Kullanım: bash test-system.sh

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       Turtle-ID Multi-Agent System - Health Check             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="http://localhost:3000"
IMAGE_ANALYSIS_URL="http://localhost:5000"
DATABASE_URL="http://localhost:5001"
TIMEOUT=5

# Helper functions
check_endpoint() {
    local name=$1
    local url=$2
    
    echo -n "Checking $name... "
    
    if response=$(curl -s -w "\n%{http_code}" -m $TIMEOUT "$url" 2>/dev/null); then
        http_code=$(echo "$response" | tail -n 1)
        
        if [ "$http_code" = "200" ]; then
            echo -e "${GREEN}✓ Healthy${NC}"
            return 0
        else
            echo -e "${RED}✗ HTTP $http_code${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ Connection failed${NC}"
        return 1
    fi
}

check_database() {
    echo -n "Checking MySQL Database... "
    
    if mysql -u turtle_user -pturtle_password -h localhost turtle_id_db -e "SELECT 1;" &>/dev/null; then
        echo -e "${GREEN}✓ Connected${NC}"
        
        # Count records
        count=$(mysql -u turtle_user -pturtle_password -h localhost turtle_id_db -se "SELECT COUNT(*) FROM turtles;" 2>/dev/null)
        echo "  └─ Turtles in DB: $count"
        return 0
    else
        echo -e "${RED}✗ Connection failed${NC}"
        return 1
    fi
}

# Test health endpoints
echo -e "${BLUE}═══ Agent Health Checks ═══${NC}"
echo ""

check_endpoint "Backend Coordinator" "$BACKEND_URL/health" || exit 1
check_endpoint "Image Analysis Agent" "$IMAGE_ANALYSIS_URL/health" || exit 1
check_endpoint "Database Agent" "$DATABASE_URL/health" || exit 1

echo ""
echo -e "${BLUE}═══ Agent-Specific Checks ═══${NC}"
echo ""

check_endpoint "Gatekeeper Agent" "$BACKEND_URL/api/validation/health" || exit 1
check_endpoint "Biolytics Agent" "$IMAGE_ANALYSIS_URL/api/biolytics/health" || exit 1
check_endpoint "Matching Agent" "$BACKEND_URL/api/matching/health" || exit 1
check_endpoint "Reporter Agent" "$BACKEND_URL/api/reporting/health" || exit 1

echo ""
echo -e "${BLUE}═══ Database Check ═══${NC}"
echo ""

check_database || exit 1

echo ""
echo -e "${BLUE}═══ Running Integration Tests ═══${NC}"
echo ""

if command -v node &> /dev/null; then
    cd "$(dirname "$0")/backend"
    
    if [ -f "tests/integration.test.js" ]; then
        node tests/integration.test.js
    else
        echo -e "${YELLOW}⚠ Integration test file not found${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Node.js not found in PATH${NC}"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   System Check Complete                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✓ All systems operational!${NC}"
echo ""

# Print summary
echo "🐢 Turtle-ID System Summary:"
echo "  Backend:     $BACKEND_URL"
echo "  Image Srv:   $IMAGE_ANALYSIS_URL"
echo "  Database:    $DATABASE_URL"
echo ""
echo "📚 Documentation:"
echo "  - SOLID Agents: docs/SOLID_AGENTS.md"
echo "  - API Reference: docs/API.md"
echo "  - Database: docs/DATABASE_SCHEMA.md"
echo ""
