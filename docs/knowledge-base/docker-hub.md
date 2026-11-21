# Docker Hub publication

## Current CI/CD publication

The [successful CI/CD run](https://github.com/Sa3d-99/Gazebo_ROS2_Web_Simulation/actions/runs/44956368322)
built source `71e557ec901e11b3d54c0373b4492dbc8c72cc0b`, passed all 19 runtime
checks for each edition and published the tested images to both registries.
Both images target Linux amd64. Anonymous manifest and configuration reads
confirmed public access, matching digests across registries and the tested
source revision in each image's labels.

| Edition | Docker Hub | GitHub Container Registry | Manifest digest in both registries |
|---|---|---|---|
| Ubuntu 22.04 / Humble / Fortress | `sa3d99/gazebo-ros2-web:ubuntu22.04` | `ghcr.io/sa3d-99/gazebo-ros2-web-ubuntu22.04:latest` | `sha256:3949c1144fade274d5e6365cf36af7434102710de3558d1462a8013c12c7159c` |
| Ubuntu 24.04 / Jazzy / Harmonic | `sa3d99/gazebo-ros2-web:ubuntu24.04` | `ghcr.io/sa3d-99/gazebo-ros2-web-ubuntu24.04:latest` | `sha256:72e9d0b789907d2c04443553f6900b72bcd450b73cdfa648d0c9e8aa4ac88bd5` |

The Humble configuration digest is
`sha256:e900ae25c4a792e3fe0dad88a2479be2fb50f64acdfeca9c069e7c3e9659e71c`;
the Jazzy configuration digest is
`sha256:5555549c039145f42f14514d27f33017e8014e13df8813b6d58aa6066eea1ffb`.
The staging-job push digests match the manifests above: publication copied the
tested images rather than rebuilding them.

```bash
docker pull sa3d99/gazebo-ros2-web:ubuntu22.04
docker pull sa3d99/gazebo-ros2-web:ubuntu24.04
```

For the exact tested Jazzy build, use its digest:

```bash
docker pull sa3d99/gazebo-ros2-web@sha256:72e9d0b789907d2c04443553f6900b72bcd450b73cdfa648d0c9e8aa4ac88bd5
```

The moving Ubuntu/ROS tags update after successful `main` builds. Commit tags
record this publication in both registries; see the [CI/CD guide](../ci-cd.md#image-tags)
for naming and versioned releases. The old Docker Hub `:tagname` tag is historical
and is not updated by this pipeline. No new local image download was required
to implement or verify CI/CD. AWS and RunPod deployment remain untested.

## Initial Docker Hub publication — 2026-11-17

The initial locally tested images were published for Linux amd64:

| Image | Edition | Digest |
|---|---|---|
| `sa3d99/gazebo-ros2-web:ubuntu22.04` | Ubuntu 22.04 / Humble / Fortress | `sha256:8511526ecbddb4d815ef216dd5f8ac6841711db51721989e71243971d70f344e` |
| `sa3d99/gazebo-ros2-web:ubuntu24.04` | Ubuntu 24.04 / Jazzy / Harmonic | `sha256:fb4a80e7d973e96c1485937d03face638c3deda744e4a91e6caa23b3d5de030a` |

Both pushes and remote manifest reads succeeded. These are the earlier locally
tested editions recorded in [validation](validation.md).

Use an image reference in the [AWS EC2 run instructions](../docker.md#run-later-on-aws-ec2).
AWS deployment remains untested.

## Initial GitHub Packages publication — 2026-11-17

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
