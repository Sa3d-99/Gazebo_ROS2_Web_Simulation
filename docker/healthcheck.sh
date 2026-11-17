#!/usr/bin/env bash
set -euo pipefail
xdpyinfo -display "${DISPLAY_NUM:-:1}" >/dev/null 2>&1
curl --fail --silent --max-time 3 "http://127.0.0.1:${WEB_PORT:-8080}/vnc.html" >/dev/null
# A served HTML page alone does not establish a working VNC desktop.
exec 3<>"/dev/tcp/127.0.0.1/${VNC_PORT:-5900}"
IFS= read -r -t 2 banner <&3
[[ "$banner" == RFB* ]]
exec 3<&-
exec 3>&-
pid="$(cat "${LOG_DIR:-/workspace/gazebo-novnc-logs}/gazebo-gui.pid")"
[[ "$pid" =~ ^[0-9]+$ && "$pid" -gt 1 ]]
kill -0 "$pid"
