# Validation evidence

Recorded 2026-10-28. Separate inherited runtime evidence from checks of this standalone repository.

The [saved integration results](evidence/gazebo-integration-2026-10-28.json) come from the combined implementation in `runpod_noVNC_isaac_sim` at `b924bd0`. Clean Docker tests passed for Ubuntu 22.04 / Humble / Fortress and Ubuntu 24.04 / Jazzy / Harmonic: package installation, noVNC HTTP 200, visibly rendered shapes world, simulator topics, mismatched-distro rejection without desktop shutdown, simulator-only stop, idempotent restart, and full desktop stop. Both used official `ros2-apt-source` 1.3.0.

Those tests preceded the separation. They do not establish a new full install/render test of this standalone checkout. The original Ubuntu 22.04 Isaac stub checks are historical provenance and do not describe an application path in this project.

At project separation, Bash syntax passed for the five application scripts and all nine then-current unittest methods passed:

```bash
bash -n bootstrap.sh install.sh novnc.sh gazebo.sh stop.sh
python3 -m unittest discover -s tests -v
```

Six methods cover platform selection/rejection, invalid ROS rejection before apt or desktop commands, recorded-session shutdown isolation, and missing/stale/invalid PIDs. Three entrypoint methods use isolated fixtures and mocked services: a fake archive verifies the new bootstrap URL and ROS environment; mocked packages verify installation always selects Gazebo; and the actual desktop shell verifies default Gazebo launch, display, world arguments, PID, and URL against mocked desktop/TCP services. These are source/entrypoint tests, not a new full Docker install/render run.

The scripts contain no Isaac, simulator-selection, or old repository path. At separation, the compatibility selector, package-presence check, and Gazebo installation functions were byte-for-byte unchanged from the previously Docker-validated implementation. The later installer-progress/cache fix changes the installation path; the inherited Docker evidence does not validate those changes. Bootstrap destination and log defaults are independent. The hosted CI workflow is defined for Ubuntu 22.04 and 24.04; no completed hosted run is claimed.

The earlier disposable containers and newly downloaded Ubuntu images were removed after integration testing. No global prune ran and preexisting Docker resources and host ROS/Gazebo were preserved. Project separation performs no new Docker downloads. Actual RunPod proxy access was not tested.

Graph extraction uses source AST and local host-agent semantic extraction. Token usage is unavailable, not a measured zero; no paid extraction API is used. The graph integrity diagnostic found no missing/dangling endpoints, self-loops, or collapsed edges; the graph freshness check completed.

## Installer-progress and cache fix

The [investigation note](installer-progress.md) records the user-supplied pod failure, the cache-race hypothesis, and the local regression scope. All 14 current unittest methods passed in 20.762 seconds: the nine updated compatibility/lifecycle/entrypoint cases and five new installer-progress cases. All six Bash scripts, including `install-utils.sh`, parse; README/TEMPLATE shell snippets and local links also pass. No new OS image, ROS/Gazebo package, or Docker download was performed for this change. The user's pod is not directly accessible, and no remote repair or successful pod rerun is claimed.

The new tests verify visible stdout/stderr and persisted failure logs, nonzero package-failure propagation without completion messages, cleanup of private archives, serialized installers, rejection of missing bridge packages, and survival when a fixture removes the default apt archive cache during a simulated download. Entrypoint fixtures also check bootstrap scratch cleanup and installer failure-log reporting.

A read-only check exercised the real private-cache apt wrapper with `--simulate --no-upgrade install -y curl ca-certificates`; it passed without downloading or installing packages. `gazebo_verify_installation` also passed against the host's already-existing Humble setup, locating `ros2`, `ros_gz_sim`, and `ros_gz_bridge`. These checks do not establish a fresh full installation or rendering run for the changed installer, either supported OS edition, or the user's pod. The exact cause of the supplied apt rename error remains unproven.
