# Gazebo compatibility and decisions

The container's `/etc/os-release` determines the only supported combinations:

| Container OS | ROS distro | Gazebo release |
|---|---|---|
| Ubuntu 22.04 / Jammy | Humble | Fortress |
| Ubuntu 24.04 / Noble | Jazzy | Harmonic |

An unset `ROS_DISTRO` is filled from Ubuntu. A conflicting distro or another OS/version is rejected before apt installation or desktop cleanup. The host OS does not determine compatibility. The source follows the [official ROS/Gazebo pairings](https://gazebosim.org/docs/latest/ros_installation/).

`gazebo.sh` provides sourceable compatibility, installation, launch, and shutdown functions plus `check`, `install`, `launch`, and `stop` commands. The desktop scripts reuse these helpers.

Installation uses `ros-<distro>-ros-base`, `ros-<distro>-ros-gz`, and Mesa/GL, Qt/XCB, and D-Bus dependencies. Installed packages and a usable existing ROS apt source are reused. Otherwise the maintained `ros2-apt-source` package configures the ROS repository. No Gazebo Classic or separate OSRF repository is added.

Launch sources `/opt/ros/<distro>/setup.bash`, selects Qt XCB, and runs `ros2 launch ros_gz_sim gz_sim.launch.py` on the shared display. `GAZEBO_ARGS` defaults to `-r shapes.sdf` and can select another world. The recorded process group and ROS launch shutdown option keep server and GUI lifecycle together.

The project installs ROS integration packages. Robot topic bridging still requires a world-specific `ros_gz_bridge` configuration. `LIBGL_ALWAYS_SOFTWARE=1` is a documented graphics fallback.

Gazebo logs and its session PID live in `LOG_DIR`, defaulting to `/workspace/gazebo-novnc-logs`. See [validation evidence](validation.md) before interpreting inherited integration results as new tests.
