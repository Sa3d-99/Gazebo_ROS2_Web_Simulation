# Separation provenance

The Gazebo implementation originated in [runpod_noVNC_isaac_sim](https://github.com/Sa3d-99/runpod_noVNC_isaac_sim) at commit `b924bd0`, which supported both simulators. The user requested two separate projects.

This repository receives the Gazebo helper, compatible desktop transport, unit tests/CI, and saved Docker results. Its bootstrap repository/destination and log directory are independent, and its scripts contain no Isaac launch or shutdown path. The original repository restores its application scripts and original user documentation from `cfdca8f` through a forward commit.

The saved Docker results are inherited from the combined implementation. Their original records, including its Isaac stub checks, remain unchanged inside the evidence JSON; added provenance metadata explains their scope. Standalone source/separation checks are recorded separately in [validation](validation.md).
