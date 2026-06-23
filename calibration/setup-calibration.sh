#!/bin/bash

# Install Weston Wayland Compositor which has the calibrator
sudo apt install weston

# Create .config folder to hold weston config
mkdir -p ~/.config

# Write Weston config
cp ./weston.ini ~/.config/weston.ini

# Write Weston calibration save script
sudo cp ./weston-save-calibration.sh /usr/bin/weston-save-calibration.sh
