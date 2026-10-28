#!/usr/bin/env bash
# Download Gazebo_ROS2_Web_Simulation without git, then install and start Gazebo.
# ROS_DISTRO is optional: Humble on Ubuntu 22.04; Jazzy on Ubuntu 24.04.
# Env overrides (WEB_PORT, RES, VNC_PASSWORD, ROS_DISTRO, GAZEBO_ARGS) pass through.
set -euo pipefail

REPO="${REPO:-Sa3d-99/Gazebo_ROS2_Web_Simulation}"
BRANCH="${BRANCH:-main}"
DEST="${DEST:-/workspace/Gazebo_ROS2_Web_Simulation}"

log() { echo "[bootstrap] $*"; }
die() { echo "[bootstrap] ERROR: $*" >&2; exit 1; }

# --- fetch the repo without git -------------------------------------------------
command -v curl >/dev/null 2>&1 || command -v wget >/dev/null 2>&1 \
    || die "neither curl nor wget is available — cannot download the repo."

TARBALL="https://codeload.github.com/${REPO}/tar.gz/refs/heads/${BRANCH}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

log "Downloading ${REPO}@${BRANCH} (no git required)..."
if command -v curl >/dev/null 2>&1; then
    curl -fL --progress-bar --retry 3 --connect-timeout 30 "$TARBALL" -o "$TMP/repo.tar.gz" \
        || die "download failed: $TARBALL"
else
    wget --progress=bar:force -O "$TMP/repo.tar.gz" "$TARBALL" || die "download failed: $TARBALL"
fi

tar -xzf "$TMP/repo.tar.gz" -C "$TMP" || die "could not extract the archive."
SRC="$(find "$TMP" -maxdepth 1 -type d -name '*-'"${BRANCH}" | head -1)"
[[ -n "$SRC" ]] || die "unexpected archive layout."

mkdir -p "$(dirname "$DEST")"
rm -rf "$DEST"
mv "$SRC" "$DEST"
chmod +x "$DEST"/*.sh 2>/dev/null || true
log "Installed to $DEST"
rm -rf "$TMP"
trap - EXIT

# --- run the method -------------------------------------------------------------
cd "$DEST"
exec bash ./novnc.sh
