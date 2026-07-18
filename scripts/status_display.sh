#!/bin/bash

echo
echo "========== DISPLAY STATUS =========="

echo
echo "Xvfb"
ps -ef | grep Xvfb | grep -v grep

echo
echo "Openbox"
ps -ef | grep openbox | grep -v grep

echo
echo "x11vnc"
ps -ef | grep x11vnc | grep -v grep

echo
echo "noVNC"
ps -ef | grep websockify | grep -v grep

echo
echo "Chromium"
ps -ef | grep chromium | grep -v grep

echo
echo "Resolution"
DISPLAY=:99 xdpyinfo | grep dimensions

echo
echo "===================================="
