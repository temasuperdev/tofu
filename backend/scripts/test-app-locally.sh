#!/bin/bash
# Тестирование Flask приложения локально

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🧪 TESTING FLASK APPLICATION (PRE-DEPLOYMENT CHECK)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

# Step 1: Check Python
echo -e "${BLUE}[1/5] Checking Python environment...${NC}"
python3 --version || { echo -e "${RED}Python 3 not found${NC}"; exit 1; }

# Step 2: Install dependencies
echo -e "${BLUE}[2/5] Installing dependencies...${NC}"
pip install -q -r requirements.txt 2>/dev/null || {
  echo "Installing with pip..."
  pip install -r requirements.txt
}
pip install -q pytest pytest-cov 2>/dev/null || pip install pytest pytest-cov

# Step 3: Run tests
echo -e "${BLUE}[3/5] Running unit tests...${NC}"
python -m pytest tests/ -v --tb=short || {
  echo -e "${RED}Tests failed${NC}"
  exit 1
}

# Step 4: Run app locally
echo -e "${BLUE}[4/5] Starting application...${NC}"
python src/app.py &
APP_PID=$!
sleep 2

# Step 5: Health check
echo -e "${BLUE}[5/5] Checking health endpoint...${NC}"
HEALTH=$(curl -s http://localhost:5000/api/health)
kill $APP_PID 2>/dev/null || true

if echo "$HEALTH" | grep -q "ok\|healthy"; then
  echo -e "${GREEN}✅ All tests passed!${NC}\n"
  echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
  echo -e "${GREEN}  Application is ready for deployment${NC}"
  echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}\n"
  exit 0
else
  echo -e "${RED}❌ Health check failed${NC}"
  exit 1
fi
