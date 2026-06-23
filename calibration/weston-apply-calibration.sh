#!/bin/bash

# ---------------------------------------------------------------------------
# Must be run as root
# ---------------------------------------------------------------------------
if [ "$EUID" -ne 0 ]; then
    echo "Error: please run this script as root." >&2
    exit 1
fi

#!/bin/bash

SRC_FILE="/tmp/.touchscreen-calibration-matrix"
RULE_FILE="/etc/udev/rules.d/99-touchscreen-calibration.rules"

if [ ! -f "$SRC_FILE" ]; then
    echo "No calibration file found: $SRC_FILE"
    exit 1
fi

MATRIX=$(cat "$SRC_FILE")

echo "Applying matrix: $MATRIX"

cat > "$RULE_FILE" <<EOF
SUBSYSTEM=="input", ENV{ID_INPUT_TOUCHSCREEN}=="1", ENV{LIBINPUT_CALIBRATION_MATRIX}="$MATRIX 0 0 1"
EOF

udevadm control --reload-rules
udevadm trigger

echo "Calibration applied"