# Validation evidence

## CI/CD pipeline implementation

`.github/workflows/ci-cd.yml` replaces the independent script-check, manual
Docker-test and per-edition publisher workflows. CI checks every Bash file,
workflow definitions, documentation links/examples and unit tests. Container
changes test both supported images; documentation-only changes skip the large
builds. Pull requests cannot publish. Trusted builds stage passed images under
commit tags; moving release tags wait for both editions and all checks.

Local validation passed all 14 unit tests in 20.770 seconds, workflow linting
with checksum-verified actionlint 1.7.12, 45 documentation Bash examples and 55
local links. Isolated executions of the actual workflow shell blocks passed six
release-planning scenarios, nine changed-path scenarios and nine final-gate
success/failure scenarios. Registry metadata reads verified the digest formatter
used by the publication job without downloading image layers.

The owner configured `DOCKERHUB_TOKEN`; its presence was checked through secret
metadata without reading its value. CD is scoped to GHCR and Docker Hub image
delivery, as requested. No cloud instance or Pod deployment is configured.
Hosted execution is verified separately from these local checks.

## Cloud setup documentation — 2026-11-17

The README now places both editions' start/stop/restart commands first and gives
numbered EC2 and RunPod setup steps. EC2 covers an x86 Ubuntu server, SSH key and
network settings, Docker's official apt repository, group-login refresh, image
startup, browser tunneling and instance stop/resume. RunPod covers template
fields, preserved image entrypoint with CMD `desktop`, deployment, HTTP 8080,
Pod lifecycle controls and `/workspace` persistence.

Provider instructions were checked against the linked official AWS, Docker and
RunPod documentation. Documentation Bash snippets and local heading links were
validated. This documentation change performs no new cloud deployment or image
download; the runtime validation and untested targets below remain unchanged.

## Standalone Docker and GitHub Packages — 2026-11-17

Both supported editions were built and tested on Linux amd64: Ubuntu 22.04 /
Humble / Fortress and Ubuntu 24.04 / Jazzy / Harmonic.

Each local edition passed 19 real container checks, including HTTP and WebSocket
access, ROS integration packages, advancing simulation statistics, a rendered
Gazebo window, offline startup, persistent worlds, VNC authentication, restart,
service failure detection and graceful shutdown. Both desktop captures were
visually inspected and showed the shapes world. Software rendering used a
1280×720 display with 1 GiB shared memory. All eight application inputs in each
local image matched the source by SHA-256.

The [GitHub package workflow](https://github.com/Sa3d-99/Gazebo_ROS2_Web_Simulation/actions/runs/44130085812)
for source commit `8648791a055f482e8245ac8399bc05e8c3e629d4` also completed
successfully. It independently built both editions, passed all 19 container
checks for each, published two public packages and saved registry receipts.
Anonymous registry reads verified that each published image's configuration
digest matches the image that passed its hosted tests.

| Hosted edition | Tested image configuration digest |
|---|---|
| Humble / Ubuntu 22.04 | `sha256:169052c85f8b40b8acfa30c027c199b94f5d1224609055d6b56696bb5f0eb174` |
| Jazzy / Ubuntu 24.04 | `sha256:6532f54a9e5fab44e467883ed9bd887f8c0eb2cb5169e045ed8dc5fe8c0f7b9f` |

The [script checks](https://github.com/Sa3d-99/Gazebo_ROS2_Web_Simulation/actions/runs/44130085806)
also passed on both Ubuntu runner versions. All 14 local unittest methods passed
in 20.765 seconds. Bash syntax, workflow YAML and shell syntax, Compose settings,
documentation commands and local links passed.

See the [publication record](docker-hub.md) for Docker Hub and GHCR references
and verified registry digests. Local images, screenshots and generated result
files are disposable and are removed after publication at the user's request;
test source and this authored record remain. Workflow evidence is available
through the linked successful run.

AWS deployment, RunPod proxy access, ARM/Graviton and hardware GPU rendering
remain untested. The small bundled world is a functional validation baseline,
not a performance benchmark. Builds fetch current packages, so use a registry
digest when an exact deployment is required.

## Storage cleanup — 2026-11-17

After registry publication was verified, removed the two local project images
(five tags) and all 26 identified build-cache records from this session. The
filesystem gained approximately 17.65 GiB. Other preexisting image IDs, cache
record IDs and container IDs were checked and preserved. The test's disposable
containers and volumes had already been removed by the smoke runner.

Generated local test JSON/PNG files are removed from the source tree and ignored
for future runs. Temporary logs, Python bytecode and generated Graphify/Obsidian
exports are disposable; authored notes, source, test scripts and published
registry images remain. The graph can be rebuilt from source on the next task.

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
