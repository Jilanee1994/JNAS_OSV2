#!/bin/bash

cd ~/JNAS-os

source ai-env/bin/activate

echo "Starting display..."
./scripts/start_display.sh

sleep 5

echo "Starting Chromium..."
DISPLAY=:99 chromium \
  --user-data-dir=$HOME/chrome-profile \
  --no-sandbox \
  >/tmp/chromium.log 2>&1 &

echo ""
echo "==================================="
echo "JNAS AI Environment Ready"
echo "==================================="
echo "Open:"
echo "http://YOUR_VM_IP:6080/vnc.html"
