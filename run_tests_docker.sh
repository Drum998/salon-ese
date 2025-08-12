#!/bin/bash
# Salon ESE Comprehensive Test Runner - Docker Script
# =================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Container name (adjust if different)
CONTAINER_NAME="salon-ese-web-1"

echo -e "${BLUE}🧪 Salon ESE Comprehensive Test Runner${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check if Docker container is running
if ! docker ps | grep -q $CONTAINER_NAME; then
    echo -e "${RED}❌ Error: Docker container '$CONTAINER_NAME' is not running${NC}"
    echo ""
    echo "To start the container, run:"
    echo "  docker-compose up -d"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Docker container '$CONTAINER_NAME' is running${NC}"
echo ""

# Function to show usage
show_usage() {
    echo "Usage:"
    echo "  ./run_tests_docker.sh                    # Run all tests"
    echo "  ./run_tests_docker.sh core               # Run core tests only"
    echo "  ./run_tests_docker.sh admin              # Run admin tests only"
    echo "  ./run_tests_docker.sh hr                 # Run HR tests only"
    echo "  ./run_tests_docker.sh ui                 # Run UI tests only"
    echo "  ./run_tests_docker.sh analytics          # Run analytics tests only"
    echo "  ./run_tests_docker.sh integration        # Run integration tests only"
    echo "  ./run_tests_docker.sh smoke              # Run smoke tests"
    echo "  ./run_tests_docker.sh dev                # Run development tests"
    echo "  ./run_tests_docker.sh prod               # Run production tests"
    echo "  ./run_tests_docker.sh pytest             # Run pytest tests only"
    echo "  ./run_tests_docker.sh help               # Show this help"
    echo ""
    echo "Examples:"
    echo "  ./run_tests_docker.sh smoke              # Quick validation"
    echo "  ./run_tests_docker.sh dev                # Development testing"
    echo "  ./run_tests_docker.sh prod               # Full production test suite"
    echo ""
}

# Check arguments
if [ $# -eq 0 ]; then
    # No arguments - run all tests
    echo -e "${YELLOW}🚀 Running ALL tests...${NC}"
    docker exec -it $CONTAINER_NAME python comprehensive_test_runner.py
elif [ "$1" = "help" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_usage
elif [ "$1" = "pytest" ]; then
    echo -e "${YELLOW}🔬 Running pytest tests with coverage...${NC}"
    docker exec -it $CONTAINER_NAME python comprehensive_test_runner.py --pytest
elif [ "$1" = "smoke" ] || [ "$1" = "dev" ] || [ "$1" = "prod" ]; then
    echo -e "${YELLOW}🎯 Running $1 preset tests...${NC}"
    docker exec -it $CONTAINER_NAME python comprehensive_test_runner.py --preset $1
elif [ "$1" = "core" ] || [ "$1" = "admin" ] || [ "$1" = "hr" ] || [ "$1" = "ui" ] || [ "$1" = "analytics" ] || [ "$1" = "integration" ]; then
    echo -e "${YELLOW}📂 Running $1 category tests...${NC}"
    docker exec -it $CONTAINER_NAME python comprehensive_test_runner.py --category $1
else
    echo -e "${RED}❌ Unknown test category/preset: $1${NC}"
    echo ""
    show_usage
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Test execution completed${NC}"
