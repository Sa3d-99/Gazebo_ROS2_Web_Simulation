# Gazebo ROS 2 Web Simulation

Run **Gazebo with ROS 2 in your browser** on RunPod using noVNC. The project
installs the desktop, ROS and the matching Gazebo release, then launches Gazebo
automatically. One HTTP port: **8080**.

## Choose your Ubuntu / ROS version

The Ubuntu version is the OS **inside the container**.

| Container image | ROS 2 | Gazebo |
|---|---|---|
| `ubuntu:22.04` | [Humble — start and stop commands](#humble-on-ubuntu-2204) | Fortress |
| `ubuntu:24.04` | [Jazzy — start and stop commands](#jazzy-on-ubuntu-2404) | Harmonic |

Only these combinations are accepted. If `ROS_DISTRO` is unset, the installer
selects it automatically from Ubuntu. An incompatible OS or distro is rejected
before package installation or desktop cleanup.

You need root or passwordless sudo, a writable system and internet access.
An existing matching ROS image also works; installed packages are reused.

## Humble on Ubuntu 22.04

Use image **`ubuntu:22.04`** with **ROS 2 Humble** and **Gazebo Fortress**.
Expose **8080 as HTTP**.

### First start — download and install

Run in a root terminal inside the Ubuntu 22.04 container:

```bash
apt-get update && apt-get install -y curl ca-certificates
curl -fsSL https://raw.githubusercontent.com/Sa3d-99/Gazebo_ROS2_Web_Simulation/main/bootstrap.sh | ROS_DISTRO=humble bash
```

### Start or restart after installation

```bash
cd /workspace/Gazebo_ROS2_Web_Simulation && ROS_DISTRO=humble bash novnc.sh
```

### Stop Gazebo and the browser desktop

```bash
cd /workspace/Gazebo_ROS2_Web_Simulation && bash stop.sh
```

This leaves the pod running. To stop billing, stop or terminate the pod in RunPod.

### RunPod Container Start Command

Use image `ubuntu:22.04`, expose **8080 as HTTP**, and paste this command
into the template's **Container Start Command** field:

```bash
bash -c "apt-get update && apt-get install -y curl ca-certificates && curl -fsSL https://raw.githubusercontent.com/Sa3d-99/Gazebo_ROS2_Web_Simulation/main/bootstrap.sh | ROS_DISTRO=humble bash; sleep infinity"
```

### Stop or relaunch only Gazebo

To keep the browser desktop open while stopping Gazebo:

```bash
cd /workspace/Gazebo_ROS2_Web_Simulation && bash gazebo.sh stop
```

To open Gazebo again on that existing desktop:

```bash
cd /workspace/Gazebo_ROS2_Web_Simulation && ROS_DISTRO=humble bash gazebo.sh launch
```

### Use ROS Humble from another terminal

```bash
source /opt/ros/humble/setup.bash
ros2 topic list
```

## Jazzy on Ubuntu 24.04

Use image **`ubuntu:24.04`** with **ROS 2 Jazzy** and **Gazebo Harmonic**.
Expose **8080 as HTTP**.

### First start — download and install

Run in a root terminal inside the Ubuntu 24.04 container:

```bash
apt-get update && apt-get install -y curl ca-certificates
curl -fsSL https://raw.githubusercontent.com/Sa3d-99/Gazebo_ROS2_Web_Simulation/main/bootstrap.sh | ROS_DISTRO=jazzy bash
```

### Start or restart after installation

```bash
cd /workspace/Gazebo_ROS2_Web_Simulation && ROS_DISTRO=jazzy bash novnc.sh
```

### Stop Gazebo and the browser desktop

```bash
cd /workspace/Gazebo_ROS2_Web_Simulation && bash stop.sh
```

This leaves the pod running. To stop billing, stop or terminate the pod in RunPod.

### RunPod Container Start Command

Use image `ubuntu:24.04`, expose **8080 as HTTP**, and paste this command
into the template's **Container Start Command** field:

```bash
bash -c "apt-get update && apt-get install -y curl ca-certificates && curl -fsSL https://raw.githubusercontent.com/Sa3d-99/Gazebo_ROS2_Web_Simulation/main/bootstrap.sh | ROS_DISTRO=jazzy bash; sleep infinity"
```

### Stop or relaunch only Gazebo

To keep the browser desktop open while stopping Gazebo:

```bash
cd /workspace/Gazebo_ROS2_Web_Simulation && bash gazebo.sh stop
```

To open Gazebo again on that existing desktop:

```bash
cd /workspace/Gazebo_ROS2_Web_Simulation && ROS_DISTRO=jazzy bash gazebo.sh launch
```

### Use ROS Jazzy from another terminal

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic list
```

## Open the browser desktop

Open **RunPod → Connect → HTTP Service → port 8080**. The script prints the URL
and saves it to `/workspace/gazebo-novnc-logs/novnc_url.txt`. The first package
installation can take several minutes. Gazebo opens its bundled `shapes.sdf`
world. Processes run detached so SSH disconnects do not stop them.

Full template settings are in [TEMPLATE.md](TEMPLATE.md).

## Options and other worlds

```bash
ROS_DISTRO=humble             # 22.04: humble; 24.04: jazzy; automatic if omitted
WEB_PORT=8080                 # expose as HTTP
VNC_PORT=5900                 # VNC stays on localhost
RES=1920x1080
DISPLAY_NUM=:1
VNC_PASSWORD=secret
LOG_DIR=/workspace/gazebo-novnc-logs
GAZEBO_ARGS='-r shapes.sdf'
```

Examples, run from the downloaded repository:

```bash
# Check compatibility without installing
bash gazebo.sh check

# Install dependencies without starting the desktop
bash install.sh

# Open a custom world
GAZEBO_ARGS='-r /workspace/worlds/my_world.sdf' bash novnc.sh

# Quote paths containing spaces inside GAZEBO_ARGS
GAZEBO_ARGS='-r "/workspace/worlds/my world.sdf"' bash novnc.sh

# Try software rendering if the virtual display has graphics-driver errors
LIBGL_ALWAYS_SOFTWARE=1 bash novnc.sh

# Change resolution and enable a VNC password
RES=2560x1440 VNC_PASSWORD=secret bash novnc.sh
```

## Connect your robot's ROS topics

The installer includes `ros_gz` integration packages. Configure `ros_gz_bridge`
for your robot's topics; starting Gazebo does not bridge all topics automatically.

## Troubleshooting

```bash
tail -50 /workspace/gazebo-novnc-logs/gazebo-gui.log
tail -50 /workspace/gazebo-novnc-logs/websockify.log
```

| Symptom | Check |
|---|---|
| Unsupported OS or ROS distro | Use exactly 22.04/Humble or 24.04/Jazzy inside the container. |
| Package installation fails | Use root/passwordless sudo and a writable system with internet access. |
| Browser page does not open | Expose 8080 as HTTP and check `websockify.log`. |
| Gazebo window is blank or exits | Check `gazebo-gui.log`; try `LIBGL_ALWAYS_SOFTWARE=1 bash novnc.sh`. |
| Pod restarted | Run `bash novnc.sh` again or configure the template startup command. |

The endpoint has no authentication by default. Set `VNC_PASSWORD` before
sharing access. Bootstrap replaces its downloaded checkout on rerun; store
worlds and other unique work elsewhere, such as `/workspace/worlds`.

## Files and project notes

| File | Purpose |
|---|---|
| `bootstrap.sh` | Download this repository without Git and start it. |
| `novnc.sh` | Start the browser desktop and Gazebo. |
| `install.sh` | Install the desktop and ROS/Gazebo dependencies. |
| `gazebo.sh` | Compatibility, packages, ROS environment, launch and tracked shutdown. |
| `stop.sh` | Stop Gazebo and the desktop while keeping the pod alive. |
| `TEMPLATE.md` | RunPod template settings and description. |
| `docs/knowledge-base/` | Architecture, migration and validation evidence; Graphify/Obsidian locations. |

The noVNC desktop code originated in
[runpod_noVNC_isaac_sim](https://github.com/Sa3d-99/runpod_noVNC_isaac_sim),
which remains the separate Isaac Sim project. This repository runs Gazebo.

## License

[MIT](LICENSE).
