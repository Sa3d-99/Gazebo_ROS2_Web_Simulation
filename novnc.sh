#!/usr/bin/env bash
# Run ROS 2 Gazebo on a detached Xvfb + Fluxbox + x11vnc + noVNC desktop.
# Usage: bash novnc.sh (Gazebo is always the application).
# ROS_DISTRO: humble on Ubuntu 22.04, jazzy on Ubuntu 24.04; auto if unset.
# Options: WEB_PORT=8080, VNC_PORT=5900, RES=1920x1080, DISPLAY_NUM=:1,
# VNC_PASSWORD=..., GAZEBO_ARGS='-r shapes.sdf',
# LOG_DIR=/workspace/gazebo-novnc-logs.
set -euo pipefail

WEB_PORT="${WEB_PORT:-8080}"
RES="${RES:-1920x1080}"
DISPLAY_NUM="${DISPLAY_NUM:-:1}"
LOG_DIR="${LOG_DIR:-/workspace/gazebo-novnc-logs}"
VNC_PORT="${VNC_PORT:-5900}"
mkdir -p "$LOG_DIR"

log() { echo "[novnc] $*"; }
die() { echo "[novnc] ERROR: $*" >&2; exit 1; }

# Is a TCP port accepting connections on localhost? Pure bash — deliberately does
# NOT use `ss`/`netstat`, which may be absent on minimal images.
port_open() {
    (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null && { exec 3<&-; exec 3>&-; return 0; }
    return 1
}

# Wait up to N seconds for a port to come up.
wait_port() {
    local port="$1" secs="${2:-15}"
    for _ in $(seq 1 "$secs"); do
        port_open "$port" && return 0
        sleep 1
    done
    return 1
}

# --- 1. dependencies (git, python3, Xvfb, x11vnc, fluxbox, noVNC, websockify) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ -f "$SCRIPT_DIR/gazebo.sh" && -f "$SCRIPT_DIR/install.sh" ]] \
    || die "Use the full repository: download it through bootstrap.sh or git clone."
# shellcheck source=gazebo.sh
source "$SCRIPT_DIR/gazebo.sh"
gazebo_select_platform
bash "$SCRIPT_DIR/install.sh"

# --- 2. stop our previous Gazebo session and desktop -----------------------------
log "Cleaning up any previous noVNC stack..."
LOG_DIR="$LOG_DIR" bash "$SCRIPT_DIR/gazebo.sh" stop
pkill -f "Xvfb ${DISPLAY_NUM}" 2>/dev/null || true
pkill -f "x11vnc -display ${DISPLAY_NUM}" 2>/dev/null || true
pkill -f "websockify --web=/usr/share/novnc ${WEB_PORT}" 2>/dev/null || true
sleep 2
rm -f "/tmp/.X${DISPLAY_NUM#:}-lock"
rm -rf "/tmp/.X11-unix/X${DISPLAY_NUM#:}" 2>/dev/null || true

export DISPLAY="$DISPLAY_NUM"

# --- 3. virtual display + window manager ---------------------------------------
log "Starting virtual display ${DISPLAY_NUM} at ${RES}..."
setsid Xvfb "$DISPLAY_NUM" -screen 0 "${RES}x24" +extension GLX +render -noreset \
    </dev/null >"$LOG_DIR/xvfb.log" 2>&1 &
for _ in $(seq 1 15); do
    xdpyinfo -display "$DISPLAY_NUM" >/dev/null 2>&1 && break
    sleep 1
done
xdpyinfo -display "$DISPLAY_NUM" >/dev/null 2>&1 \
    || die "Xvfb failed to start — see $LOG_DIR/xvfb.log"
log "Virtual display up."

setsid fluxbox </dev/null >"$LOG_DIR/fluxbox.log" 2>&1 &
sleep 1

# --- 4. VNC server on that display ----------------------------------------------
if [[ -n "${VNC_PASSWORD:-}" ]]; then
    x11vnc -storepasswd "$VNC_PASSWORD" "$LOG_DIR/vncpass" >/dev/null 2>&1
    AUTH=(-rfbauth "$LOG_DIR/vncpass")
    log "VNC password enabled."
else
    AUTH=(-nopw)
fi
log "Starting VNC server on localhost:${VNC_PORT}..."
setsid x11vnc -display "$DISPLAY_NUM" -forever -shared "${AUTH[@]}" \
    -rfbport "$VNC_PORT" -localhost -noxdamage \
    </dev/null >"$LOG_DIR/x11vnc.log" 2>&1 &
sleep 2
wait_port "$VNC_PORT" 15 \
    || die "x11vnc failed to bind :${VNC_PORT} — see $LOG_DIR/x11vnc.log"
log "VNC server up."

# --- 5. noVNC web front-end (HTTP + WebSocket, rides RunPod's HTTP proxy) -------
log "Starting noVNC web server on :${WEB_PORT}..."
setsid websockify --web=/usr/share/novnc "$WEB_PORT" "localhost:${VNC_PORT}" \
    </dev/null >"$LOG_DIR/websockify.log" 2>&1 &
sleep 2
wait_port "$WEB_PORT" 15 \
    || die "websockify failed to bind :${WEB_PORT} — see $LOG_DIR/websockify.log"
log "noVNC web server up."

# --- 6. launch Gazebo through the matching ROS environment ----------------------
log "Launching Gazebo ${GAZEBO_RELEASE} / ROS ${ROS_DISTRO} on ${DISPLAY_NUM}..."
setsid env DISPLAY="$DISPLAY_NUM" bash "$SCRIPT_DIR/gazebo.sh" launch \
    </dev/null >"$LOG_DIR/gazebo-gui.log" 2>&1 &
GAZEBO_PID=$!
echo "$GAZEBO_PID" > "$LOG_DIR/gazebo-gui.pid"
sleep 3
kill -0 "$GAZEBO_PID" 2>/dev/null \
    || die "Gazebo exited during launch — see $LOG_DIR/gazebo-gui.log"

# --- 7. print the REAL URL --------------------------------------------------------
# Never print a <POD_ID> placeholder — either we can build the real link or we say
# exactly how to get it. RunPod injects RUNPOD_POD_ID; fall back to parsing the
# pod id out of the SSH/hostname info if that env var is missing.
POD="${RUNPOD_POD_ID:-}"
if [[ -z "$POD" ]]; then
    # RunPod sets RUNPOD_POD_HOSTNAME like "<podid>-<suffix>"
    POD="${RUNPOD_POD_HOSTNAME:-}"
    POD="${POD%%-*}"
fi

echo ""
echo "=================================================================="
if [[ -n "$POD" ]]; then
    URL="https://${POD}-${WEB_PORT}.proxy.runpod.net/vnc.html?autoconnect=1&resize=remote"
    echo "$URL" > "$LOG_DIR/novnc_url.txt"
    echo "  noVNC desktop is UP. Open this in your browser:"
    echo ""
    echo "    $URL"
    echo ""
    echo "  (also saved to $LOG_DIR/novnc_url.txt)"
else
    echo "  noVNC desktop is UP on port ${WEB_PORT}, but the pod id is not in the"
    echo "  environment, so the exact URL can't be built here."
    echo ""
    echo "  Get it from the RunPod console: your Pod -> Connect ->"
    echo "  the HTTP Service link for port ${WEB_PORT}, then append:"
    echo "      /vnc.html?autoconnect=1&resize=remote"
    echo ""
    echo "  It looks like:"
    echo "      https://<POD_ID>-${WEB_PORT}.proxy.runpod.net/vnc.html?autoconnect=1&resize=remote"
fi
echo ""
echo "  Gazebo ${GAZEBO_RELEASE} / ROS ${ROS_DISTRO} is starting on the desktop."
echo "  Launch log: $LOG_DIR/gazebo-gui.log"
echo "=================================================================="
echo ""
log "Everything is detached (setsid) — survives terminal/SSH disconnect."
log "Logs: $LOG_DIR/{xvfb,x11vnc,websockify,fluxbox,gazebo-gui}.log"
