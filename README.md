# Gazebo ROS 2 Web Simulation

Run **Gazebo and ROS 2 in your browser** on your computer, AWS EC2 or RunPod.
The published Docker images already include ROS, Gazebo and the browser desktop.

**Go to:** [Start / stop commands](#start-and-stop-commands) ·
[Inside the RunPod terminal](#terminal-commands-inside-runpod) ·
[First start](#first-start-create-your-container) ·
[AWS setup](#aws-ec2-setup-step-by-step) ·
[RunPod setup](#runpod-setup-step-by-step) ·
[CI/CD](#cicd-pipeline)

## Choose your version

| Ubuntu inside the image | ROS 2 | Gazebo | Docker image |
|---|---|---|---|
| 22.04 | Humble | Fortress | `sa3d99/gazebo-ros2-web:ubuntu22.04` |
| 24.04 | Jazzy | Harmonic | `sa3d99/gazebo-ros2-web:ubuntu24.04` |

Choose **one** edition. Both images target Linux x86_64/amd64 and render using
CPU software rendering, so a GPU is not required.

## Start and stop commands

Run these commands on **your Docker computer or the EC2 server** after creating
its container with the [first-start commands](#first-start-create-your-container).

| Action | Ubuntu 22.04 / Humble | Ubuntu 24.04 / Jazzy |
|---|---|---|
| **Start again** | `docker start gazebo-humble` | `docker start gazebo-jazzy` |
| **Stop** | `docker stop --time 30 gazebo-humble` | `docker stop --time 30 gazebo-jazzy` |
| **Restart** | `docker restart --time 30 gazebo-humble` | `docker restart --time 30 gazebo-jazzy` |
| View startup logs | `docker logs -f gazebo-humble` | `docker logs -f gazebo-jazzy` |

Press `Ctrl+C` to leave the logs; the simulation keeps running.

For **RunPod**, use **Pods → your Pod → Start / Stop**, or **Restart Pod** in
its menu. The image starts Gazebo automatically whenever the Pod starts.

**To stop cloud compute charges:** stop the **EC2 instance** or **RunPod Pod**
in its cloud console. `docker stop` only stops the simulation. Persistent
storage can still be charged while the server is stopped.

## Terminal commands inside RunPod

In a terminal such as `root@...:/opt/gazebo-web#`, you are already inside the
container. Use the project's shell scripts there. The `docker` commands above
belong on your own computer or the EC2 host.

**Current published-image limitation:** the default Docker entrypoint monitors
noVNC and Gazebo. Stopping either service makes the monitor exit the container;
the provider may then stop or restart it. Starting the scripts again while the
monitor is active can also race with its checks. Stopping and restarting only
the desktop while keeping the same Pod terminal alive is **not supported by
the current Docker wrapper**.

These are the project's manual script commands, for a session running without
that automatic desktop monitor:

**Start noVNC and Gazebo:**

```bash
cd /opt/gazebo-web
bash novnc.sh
```

**Stop noVNC and Gazebo:**

```bash
cd /opt/gazebo-web
bash stop.sh
```

The prebuilt image normally starts both automatically. For its current default
mode, use the RunPod Start/Stop controls above. The Docker wrapper would need a
runtime change to support stopping the desktop from inside the Pod and leaving
the Pod running; this README update does not change that behavior.

The browser interface is **noVNC**. Its web page is named `vnc.html`, which is
why that filename appears in the browser URLs below.

## First start: create your container

Docker must already be installed. On AWS, complete
[steps 1–3 below](#aws-ec2-setup-step-by-step) first.
Run one edition at a time on host port 8080.

### Ubuntu 22.04 Humble and Fortress

```bash
docker pull sa3d99/gazebo-ros2-web:ubuntu22.04
docker run -d --name gazebo-humble --restart unless-stopped \
  --shm-size=1g --stop-timeout=30 \
  -p 127.0.0.1:8080:8080 \
  -v gazebo-humble-worlds:/workspace/worlds \
  -v gazebo-humble-logs:/workspace/gazebo-novnc-logs \
  sa3d99/gazebo-ros2-web:ubuntu22.04
```

### Ubuntu 24.04 Jazzy and Harmonic

```bash
docker pull sa3d99/gazebo-ros2-web:ubuntu24.04
docker run -d --name gazebo-jazzy --restart unless-stopped \
  --shm-size=1g --stop-timeout=30 \
  -p 127.0.0.1:8080:8080 \
  -v gazebo-jazzy-worlds:/workspace/worlds \
  -v gazebo-jazzy-logs:/workspace/gazebo-novnc-logs \
  sa3d99/gazebo-ros2-web:ubuntu24.04
```

The first download can take several minutes. Run `docker run` **once** to create
the container; use `docker start` afterward. Worlds and logs are saved in the
named Docker volumes.

On your own computer, open
**[the browser desktop](http://localhost:8080/vnc.html?autoconnect=1&resize=remote)**.
On AWS, create the SSH tunnel in step 5 before opening that link.

## AWS EC2 setup step by step

These steps use a new **Ubuntu EC2 server** and SSH from Linux, macOS or WSL.
The host can use Ubuntu 24.04 while either container edition runs inside it.

### Step 1 — create the EC2 server

1. Open the [AWS EC2 console](https://console.aws.amazon.com/ec2/) and choose your region.
2. Click **Launch instance** and give it a name, for example `gazebo-ros2`.
3. Select an **Ubuntu Server 24.04 LTS** AMI with **64-bit x86** architecture.
4. Choose an x86_64 instance type. `t3.large` (2 vCPUs / 8 GiB RAM) is an example
   starting point for the small demo; larger worlds need more resources. See
   [AWS's instance specifications](https://aws.amazon.com/ec2/instance-types/t3/).
5. Create or select a **key pair**. Download the `.pem` key to your computer.
6. In **Network settings**, use the default VPC and a public subnet, enable a
   public IP, and allow **SSH / TCP 22** from **My IP**. The SSH tunnel below uses
   this rule; no inbound 8080 rule is needed.
7. Set the root disk to **30 GiB** to leave room for Ubuntu, Docker and the image.
   Allow more space for your own worlds and saved data.
8. Review the configuration, click **Launch instance**, and wait for its status
   checks to pass. Copy its **Public IPv4 address**.

### Step 2 — connect from your computer

Replace `/path/to/aws-key.pem` with your downloaded key and `EC2_PUBLIC_IP` with
that instance's public address. Run this on **your computer**:

```bash
chmod 400 /path/to/aws-key.pem
ssh -i /path/to/aws-key.pem ubuntu@EC2_PUBLIC_IP
```

### Step 3 — install Docker on the EC2 server

Run the following in the **EC2 SSH terminal**. It configures Docker's official
Ubuntu package repository and installs Docker:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
exit
```

Reconnect from your computer so the new Docker group takes effect:

```bash
ssh -i /path/to/aws-key.pem ubuntu@EC2_PUBLIC_IP
```

In the EC2 terminal, check that both Docker client and server are available:

```bash
docker version
```

### Step 4 — start your simulation on EC2

In the **EC2 terminal**, run one of the first-start blocks above:

- [Ubuntu 22.04 / Humble commands](#ubuntu-2204-humble-and-fortress)
- [Ubuntu 24.04 / Jazzy commands](#ubuntu-2404-jazzy-and-harmonic)

Then check the matching container:

```bash
# Humble
docker inspect --format '{{.State.Health.Status}}' gazebo-humble
# Jazzy
docker inspect --format '{{.State.Health.Status}}' gazebo-jazzy
```

Run only the command for your edition. Wait for `healthy`; use the logs command
in the start/stop table if startup fails.

### Step 5 — open the browser desktop

Open a **second terminal on your own computer** and keep this tunnel running:

```bash
ssh -i /path/to/aws-key.pem -N -L 8080:127.0.0.1:8080 ubuntu@EC2_PUBLIC_IP
```

Now open
**[http://localhost:8080/vnc.html?autoconnect=1&resize=remote](http://localhost:8080/vnc.html?autoconnect=1&resize=remote)**
on your computer. Gazebo opens with its sample shapes world. `Ctrl+C` closes the
SSH tunnel; the cloud simulation keeps running.

### Step 6 — stop and resume later

1. In the EC2 terminal, run the matching **Stop** command from the table above.
2. To stop the cloud server too: **EC2 → Instances → select your instance →
   Instance state → Stop instance**.
3. To resume: choose **Start instance**, wait for its checks, and copy its current
   public IP. The address can change after a stop/start.
4. Reconnect with SSH, run `docker start gazebo-humble` or
   `docker start gazebo-jazzy`, and reopen the SSH tunnel using the current IP.

EBS-backed disk data survives an instance stop/start. EBS storage charges
continue while the instance is stopped. Termination can delete the root disk;
back up your work before deleting a server.

AWS references: [launch an instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html),
[connect with SSH](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-linux-inst-ssh.html),
[stop and start](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Stop_Start.html).
See [billing by instance state](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html#billing-by-instance-state)
for compute and storage charges while stopped.
Docker installation follows the [official Ubuntu instructions](https://docs.docker.com/engine/install/ubuntu/).

## RunPod setup step by step

RunPod runs the Docker image for you. Configure the Pod in its console.

### Step 1 — create a template

Open [RunPod Templates](https://console.runpod.io/user/templates) and choose
**New Template**. Fill in:

| Field | Value |
|---|---|
| Name | `Gazebo Humble` or `Gazebo Jazzy` |
| Container image for 22.04 | `sa3d99/gazebo-ros2-web:ubuntu22.04` |
| Container image for 24.04 | `sa3d99/gazebo-ros2-web:ubuntu24.04` |
| HTTP port | `8080` — label it `Gazebo` |
| Container disk | `20 GB` starting point for the image and runtime files |
| Persistent volume mount | `/workspace` — choose a volume size for your saved worlds |
| Entrypoint | Keep the image default |
| Container start command | Keep the image default; its CMD is `desktop` |
| Environment variable | `VNC_PASSWORD` = an eight-character password you choose |

Use **one** of the two images. If a separate **CMD / arguments** field must be
filled, use `desktop` while preserving the image's entrypoint. This is the
prebuilt image's startup argument; Gazebo launches automatically.

### Step 2 — deploy the Pod

1. Save the template.
2. Open **Pods → Deploy**.
3. Choose a **CPU Pod** and its resources; this image uses software rendering.
4. Select your custom template and click **Deploy On-Demand**.
5. Wait for the image download and startup. Check the Pod logs for the desktop
   startup message.

### Step 3 — open Gazebo

1. Open your Pod's **Connect** panel.
2. Click the HTTP service for **port 8080**.
3. Add `/vnc.html?autoconnect=1&resize=remote` to that service's base URL.
4. Enter the VNC password you configured. The shapes world opens in the browser.

### Step 4 — stop, start or restart the Pod

| Action | RunPod console |
|---|---|
| **Stop** | **Pods → your Pod → Stop**, then confirm |
| **Start again** | **Pods → your Pod → Start** (play icon) |
| **Restart** | Your Pod's menu → **Restart Pod** |

The desktop starts automatically each time the Pod starts. With an already
configured RunPod CLI, the equivalent commands on your computer are:

```bash
runpodctl pod stop YOUR_POD_ID
runpodctl pod start YOUR_POD_ID
runpodctl pod restart YOUR_POD_ID
```

### Step 5 — keep your work

Save worlds under `/workspace/worlds`. A Pod volume mounted at `/workspace`
survives stop/start but is removed when that Pod is terminated. Use a network
volume or a backup if you need the data to survive Pod deletion. Persistent
storage can still be charged while the Pod is stopped.

RunPod references: [custom templates](https://docs.runpod.io/pods/templates/create-custom-template),
[Pod controls](https://docs.runpod.io/pods/manage-pods),
[storage persistence](https://docs.runpod.io/pods/storage/types).

## Open a ROS terminal

On your Docker computer or EC2 server:

```bash
# Humble
docker exec -it gazebo-humble bash
source /opt/ros/humble/setup.bash
ros2 topic list
```

```bash
# Jazzy
docker exec -it gazebo-jazzy bash
source /opt/ros/jazzy/setup.bash
ros2 topic list
```

On RunPod, open its web terminal and source `/opt/ros/humble/setup.bash` or
`/opt/ros/jazzy/setup.bash` directly. The image includes `ros_gz_bridge` for
configuring your robot's topic bridges.

## CI/CD pipeline

[CI / CD in GitHub Actions](https://github.com/Sa3d-99/Gazebo_ROS2_Web_Simulation/actions/workflows/ci-cd.yml)
automatically checks pull requests and builds/tests both Ubuntu editions for
container changes. Documentation-only edits run the faster checks. After a
successful container change on `main`, it publishes tested GHCR images. Docker Hub
publication is enabled by adding a repository secret named `DOCKERHUB_TOKEN`
with a Read & Write Docker Hub access token; the username defaults to `sa3d99`.

Both editions must pass before release tags update. Git tags such as `v1.0.0`
publish versioned images. You can also run the workflow manually, with or
without publishing. Test artifacts are kept for one day.

See [the CI/CD setup guide](docs/ci-cd.md) for the exact steps, image tags and
troubleshooting.

## More information

- [Two public GitHub container packages](docs/docker.md#github-container-packages)
- [Build images, use Compose, change worlds, view logs, or publish](docs/docker.md)
- [Install inside a plain Ubuntu container](docs/manual-install.md)
- [Architecture and validation notes](docs/knowledge-base/README.md)

## License

[MIT](LICENSE).
