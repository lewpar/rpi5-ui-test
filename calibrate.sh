#!/bin/bash
set -e

# ---------------------------------------------------------------------------
# Must be run as root (needed to read raw input events)
# ---------------------------------------------------------------------------
if [ "$EUID" -ne 0 ]; then
    echo "Error: please run this script as root." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Find ADS7846 event device
# ---------------------------------------------------------------------------
device=""
for path in /sys/class/input/event*/device/name; do
    if [ "$(cat "$path")" = "ADS7846 Touchscreen" ]; then
        event=$(basename "$(dirname "$(dirname "$path")")")
        device="/dev/input/$event"
        break
    fi
done

if [ -z "$device" ]; then
    echo "Error: ADS7846 Touchscreen not found in /sys/class/input." >&2
    exit 1
fi

echo "==> Found ADS7846 Touchscreen at $device"
echo ""

# ---------------------------------------------------------------------------
# Read touch events over 3 seconds and average the x/y values
# ---------------------------------------------------------------------------
read_touch() {
    local label="$1"
    local hold_secs=3
    echo "==> Touch the $label corner and hold for ${hold_secs} seconds..."

    local sum_x=0 sum_y=0 count=0
    local last_x last_y
    last_x=""
    last_y=""

    while IFS= read -r line; do
        if echo "$line" | grep -q "ABS_X"; then
            last_x=$(echo "$line" | awk '{print $NF}')
        fi
        if echo "$line" | grep -q "ABS_Y"; then
            last_y=$(echo "$line" | awk '{print $NF}')
        fi
        if [ -n "$last_x" ] && [ -n "$last_y" ]; then
            sum_x=$(( sum_x + last_x ))
            sum_y=$(( sum_y + last_y ))
            count=$(( count + 1 ))
            last_x=""
            last_y=""
        fi
    done < <(timeout "$hold_secs" evtest "$device" 2>/dev/null || true)

    if [ "$count" -eq 0 ]; then
        echo "Error: no touch detected." >&2
        exit 1
    fi

    RESULT_X=$(( sum_x / count ))
    RESULT_Y=$(( sum_y / count ))

    echo "    x: $RESULT_X (averaged over $count readings)"
    echo "    y: $RESULT_Y (averaged over $count readings)"
    echo ""
}

# ---------------------------------------------------------------------------
# Calibrate top-left and bottom-right corners
# ---------------------------------------------------------------------------
read_touch "TOP LEFT"
TL_X="$RESULT_X"
TL_Y="$RESULT_Y"

read_touch "BOTTOM RIGHT"
BR_X="$RESULT_X"
BR_Y="$RESULT_Y"

# ---------------------------------------------------------------------------
# Output results
# ---------------------------------------------------------------------------
echo "=============================="
echo " Calibration Results"
echo "=============================="
echo ""
echo "Kivy config line:"
echo "  hidinput,${device},invert_y=0,min_abs_x=${TL_X},max_abs_x=${BR_X},min_abs_y=${TL_Y},max_abs_y=${BR_Y}"
echo ""
echo "Individual values:"
echo "  min_abs_x = $TL_X"
echo "  max_abs_x = $BR_X"
echo "  min_abs_y = $TL_Y"
echo "  max_abs_y = $BR_Y"