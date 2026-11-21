#!/usr/bin/env bash
set -euo pipefail

# Official actionlint release, verified before execution. Nothing is installed globally.
version=1.7.12
checksum=8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
archive="actionlint_${version}_linux_amd64.tar.gz"
curl --fail --location --silent --show-error --retry 3 \
  "https://github.com/rhysd/actionlint/releases/download/v${version}/${archive}" \
  -o "$scratch/$archive"
printf '%s  %s\n' "$checksum" "$scratch/$archive" | sha256sum --check --status
tar -xzf "$scratch/$archive" -C "$scratch" actionlint
"$scratch/actionlint"
