# Validation evidence

## Standalone Docker validation — 2026-11-17

Both images were built from this standalone checkout on Linux amd64, using the
real shared installer and fresh Ubuntu base images. These results validate the
Docker image path and the installer changes, independently of the older combined
project evidence below.

| Local image | Platform | Image size (uncompressed) | Saved results | Desktop capture |
|---|---|---|---|---|
| `gazebo-ros2-web:humble` | Ubuntu 22.04 / Humble / Fortress | 4.52 GiB | [19 checks](evidence/docker-humble-2026-11-17.json) | [Rendered shapes world](evidence/docker-humble-2026-11-17.png) |
| `gazebo-ros2-web:jazzy` | Ubuntu 24.04 / Jazzy / Harmonic | 5.30 GiB | [19 checks](evidence/docker-jazzy-2026-11-17.json) | [Rendered shapes world](evidence/docker-jazzy-2026-11-17.png) |

`python3 tests/docker_smoke.py <image> --output <results.json>` checks image
health, supported platform and package versions, published HTTP 200, WebSocket
upgrade, ROS integration packages, Gazebo topics, increasing simulation
iterations, a Gazebo GUI window, a nonblank RFB desktop capture, graceful stop,
restart, nonzero exit after service failure, world persistence across containers,
startup with `--network none` and no installer, VNC password negotiation, offline
shutdown, ROS environment for custom commands, and mismatched-distro rejection.
All 19 checks passed for each edition. The captured desktops were also visually
inspected: both show the primitive shapes and ground grid. Software rendering
was enabled, with a 1280×720 virtual display and 1 GiB shared memory.

The first Jazzy test needed its diagnostic shell to source ROS before invoking
the vendored `gz` CLI; the test was corrected. No image change was needed for
that issue. The saved successful results include image IDs, package versions,
simulation samples and timestamps.

All 14 existing unittest methods passed in 20.774 seconds. Bash syntax, Compose
configuration, Dockerfile build checks, documentation shell examples and local
links passed. The new manual Docker CI workflow is defined for both editions;
no hosted workflow run is claimed. Only the test's disposable containers and
world volume are removed; the built images remain available locally.
All eight application inputs inside each final image were also compared against
the current source with SHA-256; every file matched. The confirmed Jazzy runner
and the Humble runner both returned exit code 0.

Docker Hub upload, AWS deployment, RunPod proxy access, ARM/Graviton and hardware
GPU rendering were not tested. The integration world is small; these results are
not a performance or capacity benchmark. Build downloads use current apt/pip
packages, so preserve a published digest to deploy the same image later.

The project graph and Obsidian vault were established locally and updated for
Docker deployment. Generated captures are linked here and excluded from graph
extraction. Authored notes remain in `docs/knowledge-base/`.

## Earlier validation and provenance

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
