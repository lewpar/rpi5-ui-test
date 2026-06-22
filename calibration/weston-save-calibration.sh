#!/bin/bash

OUTFILE_FILE="/tmp/.touchscreen-calibration-matrix"
MATRIX="$2 $3 $4 $5 $6 $7"

echo "$MATRIX" > "$OUTFILE_FILE"