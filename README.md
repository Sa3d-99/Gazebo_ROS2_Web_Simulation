# Gazebo ROS 2 Web Simulation

Run **Gazebo with ROS 2 in your browser** on RunPod using noVNC. The project
installs the desktop, ROS and the matching Gazebo release, then launches Gazebo
automatically. One HTTP port: **8080**.

## Choose your Ubuntu / ROS version

The Ubuntu version is the OS **inside the container**.

| Container image | ROS 2 | Gazebo |
|---|---|---|
| `ubuntu:22.04` | Humble | Fortress |
| `ubuntu:24.04` | Jazzy | Harmonic |

Only these combinations are accepted. If `ROS_DISTRO` is unset, the installer
selects it automatically from Ubuntu. An incompatible OS or distro is rejected
before package installation or desktop cleanup.

You need root or passwordless sudo, a writable system and internet access.
An existing matching ROS image also works; installed packages are reused.

## Humble on Ubuntu 22.04

Choose an Ubuntu **22.04** container and expose port **8080 as HTTP**. In a root
terminal, install curl if needed, then start the project:

```bash
apt-get update && apt-get install -y curl ca-certificates
curl -fsSL https://raw.githubusercontent.com/Sa3d-99/Gazebo_ROS2_Web_Simulation/main/bootstrap.sh | ROS_DISTRO=humble bash
```

Restart after the repository has been downloaded:

```bash
cd /workspace/Gazebo_ROS2_Web_Simulation
ROS_DISTRO=humble bash novnc.sh
```

## Jazzy on Ubuntu 24.04

Choose an Ubuntu **24.04** container and expose port **8080 as HTTP**. In a root
terminal:

```bash
apt-get update && apt-get install -y curl ca-certificates
curl -fsSL https://raw.githubusercontent.com/Sa3d-99/Gazebo_ROS2_Web_Simulation/main/bootstrap.sh | ROS_DISTRO=jazzy bash
```

Restart after the repository has been downloaded:

```bash
cd /workspace/Gazebo_ROS2_Web_Simulation
ROS_DISTRO=jazzy bash novnc.sh
```

## RunPod template / automatic startup

Create a template with either Ubuntu image from the table above. Set HTTP port
**8080** and use this **Container Start Command** for either version:

```bash
bash -c "apt-get update && apt-get install -y curl ca-certificates && curl -fsSL https://raw.githubusercontent.com/Sa3d-99/Gazebo_ROS2_Web_Simulation/main/bootstrap.sh | bash; sleep infinity"
```

Ubuntu selects the ROS distro automatically. Gazebo is the default application;
no simulator selection flag is needed. Full settings are in [TEMPLATE.md](TEMPLATE.md).

Open **RunPod → Connect → HTTP Service → port 8080**. The script prints the URL
and saves it to `/workspace/gazebo-novnc-logs/novnc_url.txt`. The first package
installation can take several minutes. Gazebo opens its bundled `shapes.sdf`
world. Processes run detached so SSH disconnects do not stop them.

## Stop and restart

```bash
cd /workspace/Gazebo_ROS2_Web_Simulation

# Stop Gazebo and the browser desktop; leave the pod running
bash stop.sh

# Start again; reuse installed packages
bash novnc.sh

# Stop only this project's Gazebo session, keeping the desktop open
bash gazebo.sh stop

# Relaunch Gazebo on the existing desktop
bash gazebo.sh launch
```

To stop billing, stop or terminate the **pod** in the RunPod console.

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

## Use ROS from another terminal

Source the matching ROS environment in an SSH terminal:

```bash
source /opt/ros/humble/setup.bash  # Ubuntu 22.04
# OR:
source /opt/ros/jazzy/setup.bash   # Ubuntu 24.04
ros2 topic list
```

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

[MIT](LICENSE). The original desktop scripts retain their copyright notice in
[LICENSE.upstream](LICENSE.upstream).
