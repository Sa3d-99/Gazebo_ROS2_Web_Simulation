#!/usr/bin/env bash
set -euo pipefail
cd /opt/gazebo-web
source ./gazebo.sh
gazebo_select_platform

if [[ "${1:-desktop}" != desktop ]]; then
    set +u
    source "/opt/ros/${ROS_DISTRO}/setup.bash"
    set -u
    exec "$@"
fi
shift || true
if (( $# )); then
    echo "Usage: desktop (configure with environment variables), or a command" >&2
    exit 2
fi

cleanup() {
    trap - TERM INT EXIT
    echo "[container] Stopping Gazebo and desktop..."
    # Startup itself may still be waiting for a service. Stop it before cleanup.
    if [[ -n "${startup_pid:-}" ]]; then
        kill "$startup_pid" 2>/dev/null || true
        wait "$startup_pid" 2>/dev/null || true
    fi
    bash ./stop.sh || true
}
trap cleanup EXIT
trap 'exit 0' TERM INT

bash ./novnc.sh &
startup_pid=$!
if wait "$startup_pid"; then
    startup_pid=""
else
    status=$?
    startup_pid=""
    tail -n 30 "${LOG_DIR}"/*.log >&2 || true
    exit "$status"
fi
echo "[container] Desktop ready: http://localhost:${WEB_PORT:-8080}/vnc.html?autoconnect=1&resize=remote"
echo "[container] Logs: ${LOG_DIR:-/workspace/gazebo-novnc-logs}"

# PID 1 stays alive and detects a failed service instead of sleeping forever.
failures=0
while true; do
    if /usr/local/bin/healthcheck.sh; then
        failures=0
    else
        failures=$((failures + 1))
        if (( failures >= 3 )); then
            echo "[container] A desktop or Gazebo service failed; see logs in ${LOG_DIR}." >&2
            tail -n 30 "${LOG_DIR}"/*.log >&2 || true
            exit 1
        fi
    fi
    sleep 5 &
    wait $!
done
