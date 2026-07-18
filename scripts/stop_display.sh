#!/bin/bash

pkill -9 chromium
pkill -9 websockify
pkill -9 x11vnc
pkill -9 openbox
pkill -9 Xvfb

rm -f /tmp/.X99-lock
rm -rf /tmp/.X11-unix/X99

echo "Display stopped."
