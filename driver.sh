#!/bin/bash
set -euo pipefail

# ---------------------------------------------------------------------------
# System config
# ---------------------------------------------------------------------------
username=$(logname | tr -d '\n')
hardware_arch=64

echo "==> Username       : $username"
echo "==> Hardware arch  : $hardware_arch"

# RPi 5 uses /boot/firmware/config.txt — symlink to /boot/config.txt for
# compatibility with the rest of this script.
if [ -f /boot/firmware/config.txt ]; then
    sudo ln -sf /boot/firmware/config.txt /boot/config.txt
fi

# Use the correct base config for 64-bit Debian 13 (>= 12.10 branch).
sudo cp -rf ./boot/config-nomal-12.10-64.txt ./boot/config.txt.bak

# ---------------------------------------------------------------------------
# Touch overlay
# ---------------------------------------------------------------------------
sudo cp ./usr/ads7846-overlay.dtb /boot/overlays/ads7846.dtbo

# ---------------------------------------------------------------------------
# Build /boot/config.txt
# RPi 5 always uses vc4-kms-v3d on Debian 13.
# ---------------------------------------------------------------------------
sudo sed -i 's/#dtoverlay=vc4-kms-v3d/dtoverlay=vc4-kms-v3d/' ./boot/config.txt.bak

# Append display/hardware settings
# hdmi_mode=87 is the custom CVT mode for the 800x480 panel.
sudo tee -a ./boot/config.txt.bak > /dev/null <<'CONF'
hdmi_force_hotplug=1
dtparam=i2c_arm=on
dtparam=spi=on
enable_uart=1
display_rotate=0
max_usb_current=1
config_hdmi_boost=7
hdmi_group=2
hdmi_mode=87
hdmi_drive=1
hdmi_cvt 800 480 60 6 0 0 0
dtoverlay=ads7846,cs=1,penirq=25,penirq_pull=2,speed=50000,keep_vref_on=0,swapxy=0,pmax=255,xohms=150,xmin=200,xmax=3900,ymin=200,ymax=3900
CONF

sudo cp -f ./boot/config.txt.bak /boot/config.txt

# ---------------------------------------------------------------------------
# cmdline.txt — append video mode if not already present
# RPi 5 uses /boot/firmware/cmdline.txt (single line, space-separated).
# ---------------------------------------------------------------------------
CMDLINE=/boot/firmware/cmdline.txt
if ! grep -q "video=HDMI-A-1:800x480@60" "$CMDLINE"; then
    echo "==> Adding video=HDMI-A-1:800x480@60 to $CMDLINE"
    sudo sed -i 's/$/ video=HDMI-A-1:800x480@60/' "$CMDLINE"
else
    echo "==> video=HDMI-A-1:800x480@60 already present in $CMDLINE, skipping"
fi

# ---------------------------------------------------------------------------
# Record installation marker
# ---------------------------------------------------------------------------
sudo touch ./.have_installed
echo "hdmi:resistance:5:0:800:480" > ./.have_installed

# ---------------------------------------------------------------------------
# Sync and reboot
# ---------------------------------------------------------------------------
sudo sync
sudo sync
sleep 1
echo "==> Rebooting now..."
sudo reboot