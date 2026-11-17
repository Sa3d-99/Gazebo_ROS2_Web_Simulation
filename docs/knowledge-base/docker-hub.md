# Docker Hub publication

Published on Docker Hub on 2026-11-17, both for Linux amd64:

| Image | Edition | Digest |
|---|---|---|
| `sa3d99/gazebo-ros2-web:ubuntu22.04` | Ubuntu 22.04 / Humble / Fortress | `sha256:8511526ecbddb4d815ef216dd5f8ac6841711db51721989e71243971d70f344e` |
| `sa3d99/gazebo-ros2-web:ubuntu24.04` | Ubuntu 24.04 / Jazzy / Harmonic | `sha256:fb4a80e7d973e96c1485937d03face638c3deda744e4a91e6caa23b3d5de030a` |

Both pushes and remote manifest reads succeeded. These are the locally tested
editions recorded in [validation](validation.md). The earlier `:tagname` tag is
kept as a Jazzy alias.

Pull the published tag with:

```bash
docker pull sa3d99/gazebo-ros2-web:ubuntu22.04
docker pull sa3d99/gazebo-ros2-web:ubuntu24.04
```

For an exact deployment, pull the verified digest instead:

```bash
docker pull sa3d99/gazebo-ros2-web@sha256:fb4a80e7d973e96c1485937d03face638c3deda744e4a91e6caa23b3d5de030a
```

Use this image reference in the [AWS EC2 run instructions](../docker.md#run-later-on-aws-ec2).
AWS deployment remains untested.

## GitHub Packages

Both separate packages were published by the
[successful workflow](https://github.com/Sa3d-99/Gazebo_ROS2_Web_Simulation/actions/runs/44130085812)
from commit `8648791a055f482e8245ac8399bc05e8c3e629d4`.

| Public package | Verified registry digest |
|---|---|
| `ghcr.io/sa3d-99/gazebo-ros2-web-ubuntu22.04:latest` | `sha256:ceba92c06e54efb97c682fca5a6818aef635334e6edc09ba21cb614fcb9afda5` |
| `ghcr.io/sa3d-99/gazebo-ros2-web-ubuntu24.04:latest` | `sha256:414c81a5f7c7f8c86b8ddc59f9c3c75eb20145949fc356ae8b7070cd25a9591c` |

Both allow anonymous pulls. Each also has its ROS distro tag and the immutable
source tag `sha-8648791a055f482e8245ac8399bc05e8c3e629d4`. They are linked to this
GitHub repository. Their independent builds have different digests from the
Docker Hub images; both hosted editions passed all 19 runtime checks before
publication.
