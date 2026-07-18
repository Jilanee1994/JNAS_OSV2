#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

"$SCRIPT_DIR/stop_display.sh"

sleep 2

"$SCRIPT_DIR/start_display.sh"
