#!/bin/bash
# =============================================================================
# KaliAgent Screenshot Capture Script
# =============================================================================
# Captures all 15 required documentation screenshots automatically
# 
# Requirements:
# - Firefox or Chrome with WebDriver
# - Selenium Python package
# - Dashboard running on localhost:5173
#
# Usage: ./capture_screenshots.sh
# =============================================================================

set -e

# Configuration
DASHBOARD_URL="http://localhost:5173"
OUTPUT_DIR="$(dirname "$0")/../screenshots"
DELAY=3  # Seconds to wait for page load
RESOLUTION="1920x1080"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     KaliAgent Screenshot Capture Script v1.0              ║${NC}"
echo -e "${BLUE}║     Capturing 15 documentation screenshots                ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"
echo -e "${GREEN}✓${NC} Output directory: $OUTPUT_DIR"

# Check if dashboard is running
echo -e "${YELLOW}📡${NC} Checking if dashboard is running..."
if curl -s --connect-timeout 5 "$DASHBOARD_URL" > /dev/null; then
    echo -e "${GREEN}✓${NC} Dashboard is running at $DASHBOARD_URL"
else
    echo -e "${RED}✗${NC} Dashboard is NOT running at $DASHBOARD_URL"
    echo ""
    echo "Please start the dashboard:"
    echo "  cd kali_dashboard/frontend"
    echo "  npm run dev"
    echo ""
    exit 1
fi

# Check for required tools
echo -e "${YELLOW}🔧${NC} Checking for required tools..."

if command -v firefox &> /dev/null; then
    BROWSER="firefox"
    echo -e "${GREEN}✓${NC} Firefox found"
elif command -v google-chrome &> /dev/null; then
    BROWSER="chrome"
    echo -e "${GREEN}✓${NC} Chrome found"
elif command -v chromium &> /dev/null; then
    BROWSER="chromium"
    echo -e "${GREEN}✓${NC} Chromium found"
else
    echo -e "${RED}✗${NC} No supported browser found (Firefox/Chrome/Chromium)"
    echo ""
    echo "Install Firefox:"
    echo "  sudo apt install firefox"
    echo ""
    exit 1
fi

# Check for Python screenshot tool
if command -v scrot &> /dev/null; then
    SCREENSHOT_TOOL="scrot"
    echo -e "${GREEN}✓${NC} scrot found (Linux screenshot tool)"
elif command -v import &> /dev/null; then
    SCREENSHOT_TOOL="imagemagick"
    echo -e "${GREEN}✓${NC} ImageMagick found"
else
    echo -e "${YELLOW}⚠${NC} No CLI screenshot tool found, will use Python Selenium"
    SCREENSHOT_TOOL="selenium"
    if ! python3 -c "import selenium" &> /dev/null; then
        echo -e "${YELLOW}📦${NC} Installing Selenium..."
        pip3 install selenium webdriver-manager
    fi
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                    Starting Screenshot Capture            ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Screenshot list
declare -a SCREENSHOTS=(
    "01-dashboard-overview:Dashboard Overview:/dashboard"
    "02-engagements-page:Engagements Page:/engagements"
    "03-playbooks-page:Playbooks Page:/playbooks"
    "04-tools-catalog:Tools Catalog:/tools"
    "05-settings-safety:Safety Settings:/settings"
    "06-live-monitor:Live Monitor:/live-monitor"
    "07-create-engagement:Create Engagement:/engagements/new"
    "08-execute-playbook:Execute Playbook:/playbooks/execute"
    "09-scan-results:Scan Results:/results"
    "10-pdf-report-preview:PDF Report Preview:/reports/preview"
    "11-tool-details:Tool Details:/tools/nmap"
    "12-authorization-settings:Authorization Settings:/settings/auth"
    "13-audit-logs:Audit Logs:/settings/audit"
    "14-test-coverage:Test Coverage:/reports/tests"
    "15-mobile-view:Mobile View:/dashboard?mobile=true"
)

# Capture function
capture_screenshot() {
    local filename="$1"
    local description="$2"
    local url_path="$3"
    local full_url="${DASHBOARD_URL}${url_path}"
    local output_file="${OUTPUT_DIR}/${filename}.png"
    
    echo -e "${YELLOW}📸${NC} Capturing: ${description}"
    echo -e "   URL: ${full_url}"
    echo -e "   Output: ${output_file}"
    
    # Navigate to URL
    if command -v xdotool &> /dev/null; then
        # Using xdotool + browser
        firefox --new-window "$full_url" &
        FIREFOX_PID=$!
        sleep $DELAY
        
        # Wait for page load
        sleep 2
        
        # Capture window
        if [ "$SCREENSHOT_TOOL" = "scrot" ]; then
            scrot -d 1 "$output_file"
        else
            import -window root "$output_file"
        fi
        
        # Close browser
        kill $FIREFOX_PID 2>/dev/null || true
    else
        # Using Python Selenium
        python3 << PYTHON_EOF
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time

options = Options()
options.headless = False
options.add_argument("--width=$RESOLUTION".split('x')[0])
options.add_argument("--height=$RESOLUTION".split('x')[1])

driver = webdriver.Firefox(options=options)
driver.get("$full_url")
time.sleep($DELAY)

# Take screenshot
driver.save_screenshot("$output_file")
driver.quit()

print(f"✓ Captured with Selenium")
PYTHON_EOF
    fi
    
    if [ -f "$output_file" ]; then
        SIZE=$(du -h "$output_file" | cut -f1)
        echo -e "${GREEN}✓${NC} Success! (${SIZE})"
        echo ""
        return 0
    else
        echo -e "${RED}✗${NC} Failed to capture screenshot"
        echo ""
        return 1
    fi
}

# Main capture loop
CAPTURED=0
FAILED=0

for i in "${!SCREENSHOTS[@]}"; do
    IFS=':' read -r filename description url_path <<< "${SCREENSHOTS[$i]}"
    
    echo -e "${BLUE}─────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}Screenshot $((i+1)) of ${#SCREENSHOTS[@]}${NC}"
    echo -e "${BLUE}─────────────────────────────────────────────────────────────${NC}"
    echo ""
    
    if capture_screenshot "$filename" "$description" "$url_path"; then
        ((CAPTURED++))
    else
        ((FAILED++))
    fi
    
    # Delay between captures
    if [ $i -lt $((${#SCREENSHOTS[@]}-1)) ]; then
        echo -e "${YELLOW}⏳${NC} Waiting 2 seconds..."
        sleep 2
    fi
done

# Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                    Capture Complete                       ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Captured: ${GREEN}${CAPTURED}/${#SCREENSHOTS[@]}${NC}"
echo -e "Failed:   ${RED}${FAILED}/${#SCREENSHOTS[@]}${NC}"
echo ""

if [ $CAPTURED -eq ${#SCREENSHOTS[@]} ]; then
    echo -e "${GREEN}🎉 All screenshots captured successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review screenshots in: $OUTPUT_DIR"
    echo "  2. Add annotations if needed (red boxes, arrows, numbers)"
    echo "  3. Update documentation with actual screenshot paths"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠ Some screenshots failed. Check errors above.${NC}"
    echo ""
    echo "Manual capture option:"
    echo "  firefox $DASHBOARD_URL"
    echo "  Use Shift+Ctrl+C or PrintScreen to capture"
    echo ""
    exit 1
fi
