#!/bin/bash
weston --backend=drm-backend.so --socket=wayland-0 --start-fulscreen -- ./venv/bin/python main.py