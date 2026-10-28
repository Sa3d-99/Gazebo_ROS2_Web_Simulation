# RunPod template — Gazebo ROS 2 Web Simulation

Create separate templates for the Ubuntu/ROS versions you want to offer.

| Setting | Humble template | Jazzy template |
|---|---|---|
| Name | Gazebo ROS 2 Humble Web Simulation | Gazebo ROS 2 Jazzy Web Simulation |
| Container image | `ubuntu:22.04` | `ubuntu:24.04` |
| HTTP Ports | `8080` (noVNC) | `8080` (noVNC) |
| Container Start Command | Command below | Command below |
| Volume mount | `/workspace` | `/workspace` |

Use a container running as root. The same start command works for both images:

```bash
bash -c "apt-get update && apt-get install -y curl ca-certificates && curl -fsSL https://raw.githubusercontent.com/Sa3d-99/Gazebo_ROS2_Web_Simulation/main/bootstrap.sh | bash; sleep infinity"
```

The Ubuntu version selects Humble/Fortress or Jazzy/Harmonic automatically.
Optionally set `VNC_PASSWORD`, `RES`, or `GAZEBO_ARGS` in the template's
environment variables. If you set `ROS_DISTRO`, it must match the Ubuntu image.

This file describes settings to enter in RunPod; it does not create or edit a
live template. The existing Isaac Sim template uses the separate Isaac repository.

## Template description

**Gazebo and ROS 2 with a full desktop in your browser.**

Deploy, allow the first package installation to finish, then open
**Connect → HTTP Service → port 8080**. Gazebo starts with its sample shapes
world. Use Ubuntu 22.04 for ROS Humble/Gazebo Fortress or Ubuntu 24.04 for
ROS Jazzy/Gazebo Harmonic.

The desktop survives SSH disconnects. Restart with
`cd /workspace/Gazebo_ROS2_Web_Simulation && bash novnc.sh`.
Stop the desktop with `bash stop.sh`; stop the pod in RunPod to stop billing.

Set `VNC_PASSWORD` to protect the desktop when sharing its URL.

Source and commands:
https://github.com/Sa3d-99/Gazebo_ROS2_Web_Simulation
