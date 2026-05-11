#!/usr/bin/env bash
# Install Playwright Chromium system dependencies for local/WSL environments.
#
# Usage: chmod +x setup-deps.sh && ./setup-deps.sh

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}=== Playwright E2E Environment Setup ===${NC}"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_NAME="$NAME"
    OS_ID="$ID"
fi

PACKAGE_MANAGER=""
if command -v apt-get &> /dev/null; then
    PACKAGE_MANAGER="apt"
elif command -v dnf &> /dev/null; then
    PACKAGE_MANAGER="dnf"
elif command -v pacman &> /dev/null; then
    PACKAGE_MANAGER="pacman"
else
    echo -e "${RED}Error: No supported package manager found (apt/dnf/pacman)${NC}"
    exit 1
fi

echo -e "${CYAN}Detected OS: ${OS_NAME:-Unknown} (${OS_ID:-unknown})${NC}"
echo -e "${CYAN}Package manager: ${PACKAGE_MANAGER}${NC}"

echo -e "\n${YELLOW}[1/3] Installing Node.js dependencies...${NC}"
npm install

echo -e "\n${YELLOW}[2/3] Installing Playwright Chromium + system dependencies...${NC}"
npx playwright install --with-deps chromium

echo -e "\n${YELLOW}[3/3] Verifying Playwright browser installation...${NC}"
npx playwright install --dry-run chromium 2>/dev/null || true
npx playwright --version

echo -e "\n${GREEN}=== Setup Complete ===${NC}"
echo -e "${GREEN}You can now run E2E tests with: npx playwright test${NC}"
