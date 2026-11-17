# Gazebo ROS 2 Web Simulation

Run **Gazebo and ROS 2 in your browser** with Docker. Use it on your computer,
AWS EC2 or RunPod. The images already include all required software.

## Choose your version

| Ubuntu | ROS 2 | Gazebo | Docker image |
|---|---|---|---|
| 22.04 | Humble | Fortress | `sa3d99/gazebo-ros2-web:ubuntu22.04` |
| 24.04 | Jazzy | Harmonic | `sa3d99/gazebo-ros2-web:ubuntu24.04` |

Install Docker, then follow **one** of the sections below. Both images run on
Linux x86_64/amd64 and render using the CPU, so a GPU is not required.

## Ubuntu 22.04 — start Humble and Fortress

```bash
docker pull sa3d99/gazebo-ros2-web:ubuntu22.04
docker run -d --name gazebo-humble --restart unless-stopped \
  --shm-size=1g --stop-timeout=30 \
  -p 127.0.0.1:8080:8080 \
  -v gazebo-humble-worlds:/workspace/worlds \
  -v gazebo-humble-logs:/workspace/gazebo-novnc-logs \
  sa3d99/gazebo-ros2-web:ubuntu22.04
```

Stop it and start it again later:

```bash
docker stop --time 30 gazebo-humble
docker start gazebo-humble
```

## Ubuntu 24.04 — start Jazzy and Harmonic

```bash
docker pull sa3d99/gazebo-ros2-web:ubuntu24.04
docker run -d --name gazebo-jazzy --restart unless-stopped \
  --shm-size=1g --stop-timeout=30 \
  -p 127.0.0.1:8080:8080 \
  -v gazebo-jazzy-worlds:/workspace/worlds \
  -v gazebo-jazzy-logs:/workspace/gazebo-novnc-logs \
  sa3d99/gazebo-ros2-web:ubuntu24.04
```

Stop it and start it again later:

```bash
docker stop --time 30 gazebo-jazzy
docker start gazebo-jazzy
```

## Open the simulation

Open **[the browser desktop](http://localhost:8080/vnc.html?autoconnect=1&resize=remote)**.
Gazebo starts with a world containing simple shapes.

- The first image download can take several minutes.
- Run `docker run` once. After stopping, use `docker start`.
- Run one edition at a time on port 8080.
- Worlds and logs are saved in Docker volumes and survive container removal.

## Open a ROS terminal

For Humble:

```bash
docker exec -it gazebo-humble bash
source /opt/ros/humble/setup.bash
ros2 topic list
```

For Jazzy:

```bash
docker exec -it gazebo-jazzy bash
source /opt/ros/jazzy/setup.bash
ros2 topic list
```

The image includes `ros_gz_bridge`. Configure bridges for your robot's topics
when needed; launching Gazebo does not bridge every topic automatically.

## RunPod or AWS

**RunPod:** select either Docker image from the table, expose **HTTP port 8080**,
and keep the image's default start command. Open **Connect → HTTP Service → 8080**.
See [RunPod settings](TEMPLATE.md).

**AWS EC2:** use an x86_64 instance with Docker installed. Start either edition
with the commands above, then connect through an SSH tunnel. See the
[AWS instructions](docs/docker.md#run-later-on-aws-ec2).

## GitHub Packages

Two public GitHub container packages are also available:

- Ubuntu 22.04: `ghcr.io/sa3d-99/gazebo-ros2-web-ubuntu22.04:latest`
- Ubuntu 24.04: `ghcr.io/sa3d-99/gazebo-ros2-web-ubuntu24.04:latest`

Use either image in the same Docker commands. See
[package access and publishing](docs/docker.md#github-container-packages).

## More commands

- [Build images, use Compose, change worlds, view logs, or publish](docs/docker.md)
- [Install inside a plain Ubuntu container](docs/manual-install.md)
- [Architecture and validation notes](docs/knowledge-base/README.md)

## License

[MIT](LICENSE).
