#!/bin/bash

# ---------------------------------------------------------------------------
# Must be run as root
# ---------------------------------------------------------------------------
if [ "$EUID" -ne 0 ]; then
    echo "Error: please run this script as root." >&2
    exit 1
fi

# Install Weston Wayland Compositor which has the calibrator
apt install weston

# Create .config folder to hold weston config
mkdir -p ~/.config

# Write Weston config
cp ./weston.ini ~/.config/weston.ini

# Write Weston calibration save script
cp ./weston-save-calibration.sh /usr/bin/weston-save-calibration.sh
