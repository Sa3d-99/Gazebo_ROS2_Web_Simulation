# Installer progress and apt-cache investigation

Recorded 2026-10-28 from the user's supplied RunPod logs/screenshot and current source inspection. Raw pod logs are not stored in this repository; this note preserves the reported observations and their interpretation.

The pod was Ubuntu 22.04 and exposed HTTP port 8080. Its startup command still downloaded the older Isaac repository with `SIMULATOR=gazebo`, rather than the independent Gazebo project. Installation appeared silent and was interrupted twice with Ctrl-C. Apt also reported a failed rename of a downloaded `.deb` from `/var/cache/apt/archives/partial/` into `/var/cache/apt/archives/`.

The log establishes an archive-path failure. A shared-cache cleanup race is a plausible explanation, not a proven root cause. The supplied evidence does not identify which process removed or changed that path, and interrupted runs do not establish a complete installation. The HTTP port setting does not explain this apt error.

The implementation makes installation observable: apt, curl/wget, and pip progress remain visible, and `install.sh` also appends terminal output to `LOG_DIR/install.log`. Bootstrap uses the standalone Gazebo archive and removes its download scratch directory before executing the desktop launcher. Edition-specific README/TEMPLATE commands use the current Gazebo URL.

`install-utils.sh` serializes this project's installers with a five-minute `flock` wait and creates a private `mktemp` apt archive directory containing `partial/`. Apt uses that directory, three download retries, a 300-second dpkg lock timeout, and visible output. An exit trap removes only the installation's temporary cache. Apt/dpkg's own locks remain enabled. `--fix-missing` is not used because holding back missing packages would not establish a complete simulator installation.

Success is gated on ROS setup and the presence of the `ros2` command, `ros_gz_sim`, and `ros_gz_bridge`. Failed commands retain a nonzero result and point to the persisted log; desktop launch remains downstream of successful installation. The supported Ubuntu/ROS/Gazebo combinations and simulator lifecycle are unchanged.

Passing local regression fixtures delete a simulated default apt cache during download and verify that the private archive survives. Other passing cases cover output streaming, persisted failure logs, failed-command propagation, installer serialization, bootstrap scratch cleanup, and rejection of incomplete ROS integration. These mocked tests target the failure mechanism and shell behavior; they are not a new real package-installation or RunPod proxy test. Final results are recorded in [validation](validation.md).

The user's pod cannot be accessed directly from this session. Source fixes and corrected startup instructions do not imply that the remote pod has been repaired. No new Docker/OS/Gazebo downloads are needed; previous disposable integration images and containers remain removed, and the user's `.vscode/` directory is untouched.
