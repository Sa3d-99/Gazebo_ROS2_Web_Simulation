#!/usr/bin/env bash
# Install the noVNC desktop, ROS 2 and its matching Gazebo release.
# Supported only on Ubuntu 22.04/Humble and Ubuntu 24.04/Jazzy.
# Called by novnc.sh; installed system packages are reused.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() { echo "[install] $*"; }
die() { echo "[install] ERROR: $*" >&2; exit 1; }

# Reject unsupported platforms before package installation.
# shellcheck source=gazebo.sh
source "$DIR/gazebo.sh"
gazebo_select_platform

# --- privilege check ------------------------------------------------------------
# Use passwordless sudo when the container user is not root.
SUDO=""
if [[ "$(id -u)" -ne 0 ]]; then
    if sudo -n true 2>/dev/null; then
        SUDO="sudo"
        log "Not root — using passwordless sudo for package installs."
    else
        die "Not running as root and passwordless sudo is unavailable.
       Fix by either:
         (a) using a root shell:            sudo -i     then re-run
         (b) starting the pod as root, or
         (c) pre-installing the packages listed in requirements.txt.
       Current user: $(id -un)"
    fi
fi

# Show every download/configuration step and keep the same output in a log.
# shellcheck source=install-utils.sh
source "$DIR/install-utils.sh"
LOG_DIR="${LOG_DIR:-/workspace/gazebo-novnc-logs}"
mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_DIR/install.log") 2>&1
log "ROS ${ROS_DISTRO} + Gazebo ${GAZEBO_RELEASE} installation. Log: $LOG_DIR/install.log"
install_prepare_apt

# --- system packages ------------------------------------------------------------
MISSING=()
for cmd in git python3 Xvfb x11vnc fluxbox websockify xdpyinfo; do
    command -v "$cmd" >/dev/null 2>&1 || MISSING+=("$cmd")
done
python3 -m pip --version >/dev/null 2>&1 || MISSING+=("python3-pip")
# noVNC ships web assets, not a binary — check the directory instead
[[ -d /usr/share/novnc ]] || MISSING+=("novnc")

if [[ ${#MISSING[@]} -eq 0 ]]; then
    log "All system dependencies already present."
else
    log "Installing missing: ${MISSING[*]}"
    install_apt update
    install_apt install -y \
        git \
        python3 python3-pip \
        xvfb x11vnc fluxbox \
        novnc websockify \
        x11-utils iproute2 \
        ca-certificates
    log "System packages installed."
fi

# --- python packages ------------------------------------------------------------
# Only runs if requirements.txt lists a real (non-comment) package.
REQ="$DIR/requirements.txt"
if [[ -f "$REQ" ]] && grep -qEv '^[[:space:]]*(#|$)' "$REQ"; then
    log "Installing Python requirements..."
    PIP_ARGS=(--no-input --progress-bar on)
    # Ubuntu 24.04 marks its system Python as externally managed.
    if python3 -c 'import pathlib,sys,sysconfig; sys.exit(not (pathlib.Path(sysconfig.get_path("stdlib")) / "EXTERNALLY-MANAGED").exists())'; then
        PIP_ARGS+=(--break-system-packages)
    fi
    python3 -m pip install "${PIP_ARGS[@]}" -r "$REQ"
    log "Python packages installed."
fi

gazebo_install
gazebo_verify_installation

log "Installation complete. ROS ${ROS_DISTRO} and Gazebo ${GAZEBO_RELEASE} are ready."
