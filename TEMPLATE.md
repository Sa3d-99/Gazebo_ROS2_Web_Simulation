# RunPod template — Gazebo ROS 2 Web Simulation

Create separate templates for the Ubuntu/ROS versions you want to offer.
Follow the [step-by-step RunPod setup](README.md#runpod-setup-step-by-step)
for template creation, deployment, browser access and stop/start controls.

| Setting | Humble template | Jazzy template |
|---|---|---|
| Name | Gazebo ROS 2 Humble Web Simulation | Gazebo ROS 2 Jazzy Web Simulation |
| Container image | `sa3d99/gazebo-ros2-web:ubuntu22.04` | `sa3d99/gazebo-ros2-web:ubuntu24.04` |
| HTTP Ports | `8080` (noVNC) | `8080` (noVNC) |
| Container Start Command | Keep image default | Keep image default |
| Volume mount | `/workspace` | `/workspace` |

Use a container running as root. Both images include all dependencies and start
the desktop automatically; keep the default entrypoint and command. Open
**Connect → HTTP Service → port 8080** after startup. The application lives at
`/opt/gazebo-web`, so a `/workspace` volume does not hide its scripts.

Optionally set `VNC_PASSWORD`, `RES`, or `GAZEBO_ARGS` in the template environment.
If you set `ROS_DISTRO`, it must match the Ubuntu edition. Worlds can be stored
under `/workspace/worlds`; logs are in `/workspace/gazebo-novnc-logs`.

This file describes settings to enter in RunPod; it does not create or edit a
live template. Restart or stop the pod through RunPod's controls.

## Alternative: install inside a plain Ubuntu image

For an `ubuntu:22.04` or `ubuntu:24.04` template instead of the prebuilt images,
use this Container Start Command:

```bash
bash -c "apt-get update && apt-get install -y curl ca-certificates && curl -fL --progress-bar https://raw.githubusercontent.com/Sa3d-99/Gazebo_ROS2_Web_Simulation/main/bootstrap.sh | bash; sleep infinity"
```

Use the `Gazebo_ROS2_Web_Simulation` URL shown above for this project. An old
`runpod_noVNC_isaac_sim` URL starts the separate Isaac project.

Downloads and package installation print in the terminal and are saved to
`/workspace/gazebo-novnc-logs/install.log`. Allow installation to finish.

The Ubuntu version selects Humble/Fortress or Jazzy/Harmonic automatically.
For this plain-Ubuntu installation, restart the desktop with
`cd /workspace/Gazebo_ROS2_Web_Simulation && bash novnc.sh` and stop it with
`bash stop.sh`.

## Template description

**Gazebo and ROS 2 with a full desktop in your browser.**

Deploy the prebuilt image, then open
**Connect → HTTP Service → port 8080**. Gazebo starts with its sample shapes
world. Use Ubuntu 22.04 for ROS Humble/Gazebo Fortress or Ubuntu 24.04 for
ROS Jazzy/Gazebo Harmonic.

The desktop survives SSH disconnects. Restart or stop the pod in RunPod;
stopping the desktop alone does not stop pod billing.

Set `VNC_PASSWORD` to protect the desktop when sharing its URL.

Source and commands:
https://github.com/Sa3d-99/Gazebo_ROS2_Web_Simulation
