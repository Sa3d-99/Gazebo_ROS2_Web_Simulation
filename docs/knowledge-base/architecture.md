# Architecture

The application starts Gazebo on a browser-accessible X desktop. Gazebo is the only simulator; no Isaac installation or application-selection variable is required.

```text
bootstrap.sh → novnc.sh → install.sh → gazebo.sh installation helpers
                  ├─ Xvfb + Fluxbox
                  ├─ x11vnc on localhost:5900
                  ├─ websockify + noVNC on HTTP :8080 → RunPod proxy → browser
                  └─ detached ROS launch → Gazebo GUI/server
```

`bootstrap.sh` downloads this repository's GitHub archive into `/workspace/Gazebo_ROS2_Web_Simulation`, then executes `novnc.sh`. It replaces its destination checkout on rerun, so keep unique worlds and work outside that directory.

`install.sh` validates the Ubuntu/ROS pairing before desktop installation, installs apt desktop dependencies and `websockify`, and invokes the Gazebo package helper. `install-utils.sh` centralizes visible apt output, installer serialization, and a private temporary package archive directory. Root or passwordless sudo and a writable system are required. Output is streamed to the terminal and persisted in `LOG_DIR/install.log`; ROS setup and both integration packages are verified before success is reported.

`novnc.sh` validates compatibility, installs missing dependencies, cleans up its previous session, and launches Xvfb, Fluxbox, x11vnc, websockify, and the ROS Gazebo launcher. Long-lived processes use `setsid`. The Gazebo session PID is recorded so shutdown targets its process group without a broad simulator-name match.

Defaults are display `:1`, resolution `1920x1080`, VNC `5900`, HTTP `8080`, and logs `/workspace/gazebo-novnc-logs`. The browser URL is printed and saved to `novnc_url.txt` when a RunPod identifier is available; otherwise the script gives console instructions. Set `VNC_PASSWORD` for optional VNC authentication.

`bash gazebo.sh stop` stops the recorded simulator session and keeps the desktop available. `bash stop.sh` also stops the desktop. Stopping pod billing remains a RunPod console action. This repository does not launch or kill Isaac processes.

See [compatibility decisions](gazebo.md), [provenance](migration.md), and [validation](validation.md).
