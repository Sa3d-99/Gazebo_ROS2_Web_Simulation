# Project knowledge

This repository runs ROS 2 Gazebo through a browser desktop on Docker, AWS EC2
or RunPod. It is independent of the original Isaac Sim repository and does not
require a simulator-selection flag.

- [Architecture](architecture.md)
- [Compatibility and implementation decisions](gazebo.md)
- [Separation provenance](migration.md)
- [Validation evidence and limits](validation.md)
- [Installer progress and apt-cache investigation](installer-progress.md)
- [Setup and commands](../../README.md)
- [Docker images, Docker Hub publishing and AWS EC2](../docker.md)
- [Published Docker Hub image and verified digest](docker-hub.md)
- [CI/CD pipeline and registry setup](../ci-cd.md)

Durable authored notes live here. Local Graphify data is in `graphify-out/graph.json`, the audit report in `graphify-out/GRAPH_REPORT.md`, and the interactive view in `graphify-out/graph.html`. Open `graphify-out/obsidian/` as the Obsidian vault; authored notes are incorporated under `project-knowledge/`.

Use the installed Graphify skill for source-aware incremental updates. Query with `graphify query "your question"` and verify findings against source. Keep directed edges so caller/callee relationships remain meaningful. Regenerate the vault with `graphify export obsidian`, preserving authored notes. Exports and caches remain local and are excluded from Git and extraction.

After publication on 2026-11-17, the user requested source-only local storage.
Disposable images, build caches, captures and generated graph/vault outputs are
removed; these authored notes remain. Rebuild missing Graphify/Obsidian outputs
with the installed skill when substantial project work resumes.
