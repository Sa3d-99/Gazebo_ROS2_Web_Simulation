# Validation evidence

Recorded 2026-10-28. Separate inherited runtime evidence from checks of this standalone repository.

The [saved integration results](evidence/gazebo-integration-2026-10-28.json) come from the combined implementation in `runpod_noVNC_isaac_sim` at `b924bd0`. Clean Docker tests passed for Ubuntu 22.04 / Humble / Fortress and Ubuntu 24.04 / Jazzy / Harmonic: package installation, noVNC HTTP 200, visibly rendered shapes world, simulator topics, mismatched-distro rejection without desktop shutdown, simulator-only stop, idempotent restart, and full desktop stop. Both used official `ros2-apt-source` 1.3.0.

Those tests preceded the separation. They do not establish a new full install/render test of this standalone checkout. The original Ubuntu 22.04 Isaac stub checks are historical provenance and do not describe an application path in this project.

Standalone Bash syntax passes for all five application scripts. All nine unittest methods pass:

```bash
bash -n bootstrap.sh install.sh novnc.sh gazebo.sh stop.sh
python3 -m unittest discover -s tests -v
```

Six methods cover platform selection/rejection, invalid ROS rejection before apt or desktop commands, recorded-session shutdown isolation, and missing/stale/invalid PIDs. Three entrypoint methods use isolated fixtures and mocked services: a fake archive verifies the new bootstrap URL and ROS environment; mocked packages verify installation always selects Gazebo; and the actual desktop shell verifies default Gazebo launch, display, world arguments, PID, and URL against mocked desktop/TCP services. These are source/entrypoint tests, not a new full Docker install/render run.

The scripts contain no Isaac, simulator-selection, or old repository path. The compatibility selector, package-presence check, and Gazebo installation functions are byte-for-byte unchanged from the previously Docker-validated implementation. Bootstrap destination and log defaults are independent. The hosted CI workflow is defined for Ubuntu 22.04 and 24.04; no completed hosted run is claimed.

The earlier disposable containers and newly downloaded Ubuntu images were removed after integration testing. No global prune ran and preexisting Docker resources and host ROS/Gazebo were preserved. Project separation performs no new Docker downloads. Actual RunPod proxy access was not tested.

Graph extraction uses source AST and local host-agent semantic extraction. Token usage is unavailable, not a measured zero; no paid extraction API is used. The graph integrity diagnostic found no missing/dangling endpoints, self-loops, or collapsed edges; the graph freshness check completed.
