#!/bin/bash
set -euo pipefail

# ---------------------------------------------------------------------------
# Must be run as root
# ---------------------------------------------------------------------------
if [ "$EUID" -ne 0 ]; then
    echo "Error: please run as root (sudo ./install.sh)" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# System config
# ---------------------------------------------------------------------------
username=$(logname | tr -d '\n')
hardware_arch=64

echo "==> Username       : $username"
echo "==> Hardware arch  : $hardware_arch"

# ---------------------------------------------------------------------------
# Touch overlay
# ---------------------------------------------------------------------------
cp ./ads7846-overlay.dtb /boot/overlays/ads7846.dtbo

# ---------------------------------------------------------------------------
# Build /boot/firmware/config.txt
# Written fresh each run so re-running is safe.
# hdmi_mode=87 is the custom CVT mode for the 800x480 panel.
# ---------------------------------------------------------------------------
if ! grep -q "dtoverlay=ads7846" /boot/firmware/config.txt; then
    tee -a /boot/firmware/config.txt > /dev/null <<'CONF'
 
# Added by install.sh
dtoverlay=vc4-kms-v3d
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
else
    echo "==> /boot/firmware/config.txt already configured, skipping"
fi

# ---------------------------------------------------------------------------
# cmdline.txt — append video mode if not already present
# RPi 5 uses /boot/firmware/cmdline.txt (single line, space-separated).
# ---------------------------------------------------------------------------
CMDLINE=/boot/firmware/cmdline.txt
if ! grep -q "video=HDMI-A-1:800x480@60" "$CMDLINE"; then
    echo "==> Adding video=HDMI-A-1:800x480@60 to $CMDLINE"
    sed -i 's/$/ video=HDMI-A-1:800x480@60/' "$CMDLINE"
else
    echo "==> video=HDMI-A-1:800x480@60 already present in $CMDLINE, skipping"
fi

# ---------------------------------------------------------------------------
# Record installation marker
# ---------------------------------------------------------------------------
touch ./.have_installed
echo "hdmi:resistance:5:0:800:480" > ./.have_installed

# ---------------------------------------------------------------------------
# Sync and reboot
# ---------------------------------------------------------------------------
sync
sync
sleep 1
read -rp "Press RETURN to reboot."
reboot