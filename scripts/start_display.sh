#!/bin/bash

# Stop any old processes
pkill -9 Xvfb 2>/dev/null
pkill -9 openbox 2>/dev/null
pkill -9 x11vnc 2>/dev/null
pkill -9 websockify 2>/dev/null

rm -f /tmp/.X99-lock
rm -rf /tmp/.X11-unix/X99

sleep 1

export DISPLAY=:99

echo "Starting Xvfb..."
Xvfb :99 -screen 0 1366x768x24 >/tmp/xvfb.log 2>&1 &
sleep 2

echo "Starting Openbox..."
DISPLAY=:99 openbox >/tmp/openbox.log 2>&1 &
sleep 2

echo "Starting x11vnc..."
DISPLAY=:99 x11vnc -display :99 -forever -nopw >/tmp/x11vnc.log 2>&1 &
sleep 2

echo "Starting noVNC..."
websockify --web=/usr/share/novnc 6080 localhost:5900 >/tmp/novnc.log 2>&1 &
sleep 2

echo
echo "====================================="
echo " Display Started Successfully!"
echo "====================================="
echo
echo "Display      : :99"
echo "Resolution   : 1366x768"
echo "noVNC URL    : http://YOUR_VM_IP:6080/vnc.html"
echo
