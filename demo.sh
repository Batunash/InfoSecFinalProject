#!/bin/bash

# DevSecOps Pipeline Demo Script
# This script demonstrates all security features of the pipeline

echo "=========================================="
echo "DevSecOps Pipeline Demo"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo -e "\n${YELLOW}=========================================="
    echo "$1"
    echo -e "==========================================${NC}\n"
}

# Function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
    fi
}

# 1. Project Structure
print_header "1. Project Structure"
echo "Directory structure:"
tree -L 3 -I '__pycache__|*.pyc|.git' || find . -type f -name "*.py" -o -name "*.yml" -o -name "*.yaml" -o -name "*.txt" -o -name "*.md" | head -30

# 2. Build Application
print_header "2. Building Application"
cd app
docker build -t devsecops-app:demo .
check_success "Docker image built"
cd ..

# 3. Start Application
print_header "3. Starting Application"
docker-compose up -d app
sleep 5
check_success "Application started"

# 4. Health Check
print_header "4. Health Check"
curl -s http://localhost:5000/health | python -m json.tool
check_success "Health check passed"

# 5. API Testing
print_header "5. API Testing"

echo "Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demouser","password":"password123","email":"demo@test.com"}')
echo "$REGISTER_RESPONSE" | python -m json.tool
check_success "User registered"

echo ""
echo "Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demouser","password":"password123"}')
echo "$LOGIN_RESPONSE" | python -m json.tool
check_success "User logged in"

# Extract token
TOKEN=$(echo "$LOGIN_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo ""
echo "Accessing protected endpoint..."
curl -s -X GET http://localhost:5000/api/protected \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
check_success "Protected endpoint accessed"

# 6. Unit Tests
print_header "6. Running Unit Tests"
cd app
pytest tests/ -v --cov=src --cov-report=term-missing
check_success "Unit tests passed"
cd ..

# 7. SAST with Bandit
print_header "7. Static Application Security Testing (Bandit)"
cd app
bandit -r src/ -c ../security/bandit-config.yaml || true
check_success "SAST scan completed"
cd ..

# 8. SCA with Safety
print_header "8. Software Composition Analysis (Safety)"
cd app
safety check || true
check_success "SCA scan completed"
cd ..

# 9. Container Scanning with Trivy
print_header "9. Container Image Scanning (Trivy)"
trivy image devsecops-app:demo --severity HIGH,CRITICAL || true
check_success "Container scan completed"

# 10. Code Quality Checks
print_header "10. Code Quality Checks"
cd app/src
echo "Running Black..."
black --check . || true
echo ""
echo "Running Flake8..."
flake8 . --max-line-length=100 || true
cd ../..
check_success "Code quality checks completed"

# 11. Security Summary
print_header "11. Security Summary"
echo "Security Tools Used:"
echo "  ✓ SAST: Bandit"
echo "  ✓ SCA: Safety"
echo "  ✓ Container: Trivy"
echo "  ✓ Code Quality: Black, Flake8"
echo ""
echo "Security Features Implemented:"
echo "  ✓ JWT-based authentication"
echo "  ✓ Password hashing with bcrypt"
echo "  ✓ Input validation"
echo "  ✓ Output encoding"
echo "  ✓ Security event logging"
echo ""

# 12. Cleanup
print_header "12. Cleanup"
read -p "Stop application? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose down
    check_success "Application stopped"
fi

print_header "Demo Complete!"
echo "All security features have been demonstrated."
echo ""
