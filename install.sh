#!/usr/bin/env bash
set -e

# Colored output formatting
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0;37m' # No Color

echo -e "${BLUE}=== Starting Kālayantra Installation ===${NC}"

# 1. Make python service executable
echo -e "${BLUE}[1/4] Making backend script executable...${NC}"
chmod +x contents/scripts/Kalasetu.py

# 2. Setup systemd user service
echo -e "${BLUE}[2/4] Registering systemd user service...${NC}"
USER_SYSTEMD_DIR="${HOME}/.config/systemd/user"
mkdir -p "${USER_SYSTEMD_DIR}"

# Disable and clean up legacy backend service
systemctl --user disable --now kalayantra-backend.service >/dev/null 2>&1 || true
rm -f "${USER_SYSTEMD_DIR}/kalayantra-backend.service"

SERVICE_FILE="${USER_SYSTEMD_DIR}/kalachakra.service"
cat << EOF > "${SERVICE_FILE}"
[Unit]
Description=Kālachakra Panchanga Engine
After=default.target

[Service]
Type=simple
ExecStart=$(which python3) $(pwd)/contents/scripts/Kalasetu.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

echo -e "${BLUE}[3/4] Enabling and starting systemd service...${NC}"
systemctl --user daemon-reload
systemctl --user enable kalachakra.service
systemctl --user restart kalachakra.service

# Verify service is running
if systemctl --user is-active kalachakra.service >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Kālachakra Panchanga Engine started successfully on port 8642.${NC}"
else
    echo -e "${RED}✗ Warning: Engine failed to start. Please check systemctl --user status kalachakra.service${NC}"
fi

# 3. Install Plasma 6 Plasmoid
echo -e "${BLUE}[4/4] Registering Plasmoid widget via kpackagetool6...${NC}"
# Remove existing widget to clean up previous versions
kpackagetool6 --type Plasma/Applet --remove org.kde.plasma.kalayantra >/dev/null 2>&1 || true
# Install current version
kpackagetool6 --type Plasma/Applet --install .

echo -e "${GREEN}✓ Plasmoid widget installed successfully!${NC}"
echo -e "${YELLOW}=======================================================${NC}"
echo -e "${GREEN}Installation completed!${NC}"
echo -e "${YELLOW}You can now add 'Kālayantra' to your desktop or panel.${NC}"
echo -e "${YELLOW}=======================================================${NC}"
