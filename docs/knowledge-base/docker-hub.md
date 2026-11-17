# Docker Hub publication

Published on Docker Hub on 2026-11-17, both for Linux amd64:

| Image | Edition | Digest |
|---|---|---|
| `sa3d99/gazebo-ros2-web:ubuntu22.04` | Ubuntu 22.04 / Humble / Fortress | `sha256:8511526ecbddb4d815ef216dd5f8ac6841711db51721989e71243971d70f344e` |
| `sa3d99/gazebo-ros2-web:ubuntu24.04` | Ubuntu 24.04 / Jazzy / Harmonic | `sha256:fb4a80e7d973e96c1485937d03face638c3deda744e4a91e6caa23b3d5de030a` |

These match the image IDs in the successful standalone results for
[Humble](evidence/docker-humble-2026-11-17.json) and
[Jazzy](evidence/docker-jazzy-2026-11-17.json). The earlier `:tagname` tag is kept
as a Jazzy alias. Both pushes returned exit code 0.

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
