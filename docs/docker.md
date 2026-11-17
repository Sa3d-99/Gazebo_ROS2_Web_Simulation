# Docker, Docker Hub and AWS

The image includes ROS 2, Gazebo, Xvfb, Fluxbox, x11vnc and noVNC. Dependencies
are installed during the build. Starting a container requires no package
downloads, host ROS installation, GPU or privileged mode. Software rendering is
enabled by default. The default world is the bundled `shapes.sdf`.

## Pull the published editions

```bash
docker pull sa3d99/gazebo-ros2-web:ubuntu22.04  # Humble / Fortress
docker pull sa3d99/gazebo-ros2-web:ubuntu24.04  # Jazzy / Harmonic
```

See the [README's edition-specific commands](../README.md#choose-a-prebuilt-image)
for start, stop, restart, logs and ROS terminals. The earlier `:tagname` tag is a
Jazzy alias. The [publication record](knowledge-base/docker-hub.md) saves verified
image digests.

## GitHub container packages

The repository publishes two separate packages through
[Publish container packages](../.github/workflows/publish-packages.yml):

| Edition | Package |
|---|---|
| Ubuntu 22.04 / Humble / Fortress | `ghcr.io/sa3d-99/gazebo-ros2-web-ubuntu22.04:latest` |
| Ubuntu 24.04 / Jazzy / Harmonic | `ghcr.io/sa3d-99/gazebo-ros2-web-ubuntu24.04:latest` |

The workflow builds and runs all 19 container checks before pushing an edition.
It authenticates using the repository's `GITHUB_TOKEN` with `packages: write`;
no Docker Hub secret is needed. It runs when container sources change on `main`
and can also be started manually in **Actions → Publish container packages →
Run workflow**. Each package has `latest`, its ROS distro tag, and
`sha-<full-commit>` for that source revision. GitHub builds are independent of
the local Docker Hub builds; their digests can differ.

GitHub creates container packages as private initially. The owner can make each
package public through its package page → **Package settings → Change
visibility**. For private GHCR pulls, authenticate with your GitHub username and
a personal access token (classic) with `read:packages`:

```bash
docker login ghcr.io -u Sa3d-99
docker pull ghcr.io/sa3d-99/gazebo-ros2-web-ubuntu22.04:latest
docker pull ghcr.io/sa3d-99/gazebo-ros2-web-ubuntu24.04:latest
```

Enter the token at Docker's password prompt. Public GHCR packages can be pulled
without authentication. See GitHub's [container registry documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
and [package visibility instructions](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility).

## Build and run locally

Run from the repository root with Docker Engine and the Compose plugin:

```bash
# Default: Ubuntu 24.04 / ROS Jazzy / Gazebo Harmonic
docker build -t gazebo-ros2-web:jazzy .
GAZEBO_IMAGE=gazebo-ros2-web:jazzy docker compose up -d --no-build
docker compose ps
docker compose logs -f
```

Open <http://localhost:8080/vnc.html?autoconnect=1&resize=remote>.
Compose binds the port to localhost and persists worlds and logs in named
volumes. Stop with `docker compose down`; volumes survive. `docker compose
down -v` deletes those saved volumes.

For Ubuntu 22.04 / ROS Humble / Gazebo Fortress:

```bash
docker build --build-arg UBUNTU_VERSION=22.04 -t gazebo-ros2-web:humble .
GAZEBO_IMAGE=gazebo-ros2-web:humble UBUNTU_VERSION=22.04 docker compose up -d --no-build
```

Or run without Compose:

```bash
docker run -d --name gazebo --restart unless-stopped \
  --shm-size=1g --stop-timeout=30 \
  -p 127.0.0.1:8080:8080 \
  -v gazebo-worlds:/workspace/worlds \
  -v gazebo-logs:/workspace/gazebo-novnc-logs \
  gazebo-ros2-web:jazzy
docker logs -f gazebo
docker stop --time 30 gazebo
docker start gazebo
```

Pass existing options with `-e`, for example `-e RES=1280x720`,
`-e VNC_PASSWORD=...` or `-e 'GAZEBO_ARGS=-r /workspace/worlds/my_world.sdf'`.
You can bind-mount your own worlds directory instead of a named volume.
VNC passwords use the legacy VNC scheme (only the first eight characters are
significant); use an SSH tunnel or HTTPS access gateway for remote access.

The desktop health check verifies X, HTTP, VNC and the ROS launch process.
If a required service stays down, the container exits with failure so Docker's
restart policy can recover it. Stop the whole container with `docker stop`;
`gazebo.sh stop` also makes this image's desktop supervisor exit.
Use a 30-second stop timeout to allow ROS and the desktop to shut down.

Application scripts live at `/opt/gazebo-web`, outside mounted workspaces.
Logs live at `/workspace/gazebo-novnc-logs`. To use ROS in an existing container:

```bash
docker exec -it gazebo bash
source /opt/ros/jazzy/setup.bash  # humble for the other edition
ros2 topic list
```

Commands supplied instead of `desktop` run with ROS sourced, without starting
the desktop, for example `docker run --rm gazebo-ros2-web:jazzy ros2 pkg prefix
ros_gz_bridge`. `GAZEBO_PREINSTALLED=1` skips the installer in these images;
the ROS integration installation is still checked on startup.

## Repeat the integration test

```bash
python3 tests/docker_smoke.py gazebo-ros2-web:jazzy \
  --output /tmp/gazebo-jazzy-results.json
python3 tests/docker_smoke.py gazebo-ros2-web:humble \
  --output /tmp/gazebo-humble-results.json
```

The test uses disposable containers, checks HTTP, VNC/WebSocket access, ROS
packages, active simulation topics, restart, startup without networking,
service failure and graceful shutdown. It removes only its own containers.
It needs Docker access and Python 3 on the host. See the
[validation record](knowledge-base/validation.md) for completed runs and limits.

## Upload to Docker Hub

For the existing `sa3d99/gazebo-ros2-web` repository:

```bash
docker login
docker tag gazebo-ros2-web:humble sa3d99/gazebo-ros2-web:ubuntu22.04
docker push sa3d99/gazebo-ros2-web:ubuntu22.04
docker tag gazebo-ros2-web:jazzy sa3d99/gazebo-ros2-web:ubuntu24.04
docker push sa3d99/gazebo-ros2-web:ubuntu24.04
```

Use distinct version tags such as `ubuntu24.04-v1` for releases you need to reproduce.
Builds fetch current Ubuntu/ROS packages, so rebuilding later may change package
versions. Preserve the pushed image digest for an exact deployment.
These commands follow Docker's [tag and push workflow](https://docs.docker.com/docker-hub/repos/manage/hub-images/push/).

## Run later on AWS EC2

The locally validated images target **Linux amd64**. Use an x86_64 EC2 instance
with Docker Engine installed; select an Ubuntu host if you want the familiar
tooling. Container Ubuntu/ROS versions are independent of the host version.
Choose CPU and memory for your world; the small bundled world is the validation
baseline, not a capacity benchmark. ARM/Graviton and GPU rendering have not been
validated.

The tested local images occupy approximately 5.30 GiB (Jazzy) and 4.52 GiB
(Humble) uncompressed, plus space for worlds, logs and Docker data. Registry
transfer sizes differ. See the [saved results](knowledge-base/validation.md).

After publishing, SSH into EC2 and run:

```bash
docker pull sa3d99/gazebo-ros2-web:ubuntu24.04
docker run -d --name gazebo --restart unless-stopped \
  --shm-size=1g --stop-timeout=30 \
  -p 127.0.0.1:8080:8080 \
  -v gazebo-worlds:/workspace/worlds \
  -v gazebo-logs:/workspace/gazebo-novnc-logs \
  sa3d99/gazebo-ros2-web:ubuntu24.04
docker inspect --format '{{.State.Health.Status}}' gazebo
```

For a private Docker Hub repository, run `docker login` on EC2 before pulling.
From your own computer, open an SSH tunnel:

```bash
ssh -i /path/to/aws-key.pem -L 8080:127.0.0.1:8080 ubuntu@EC2_PUBLIC_IP
```

Then open <http://localhost:8080/vnc.html?autoconnect=1&resize=remote> locally.
Allow inbound SSH/TCP 22 from your own IP in the EC2 security group; this tunnel
does not require an inbound 8080 or 5900 rule. AWS documents source-restricted
SSH rules in its [security group reference](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-rules-reference.html#sg-rules-connecting-instance).
For shared browser access, put an authenticated HTTPS reverse proxy in front
of the service with WebSocket support.

The image also works on RunPod: select your published image, expose HTTP 8080,
and keep its default entrypoint/start command. Do not use the bootstrap command
with this prebuilt image. Standalone Docker networking does not expose ROS DDS
discovery to other machines; configure ROS networking and bridges separately
if your robot runs outside this container.
