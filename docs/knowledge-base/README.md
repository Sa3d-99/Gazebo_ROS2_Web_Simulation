# Project knowledge

This repository runs ROS 2 Gazebo through a browser desktop on RunPod. It is independent of the original Isaac Sim repository and does not require a simulator-selection flag.

- [Architecture](architecture.md)
- [Compatibility and implementation decisions](gazebo.md)
- [Separation provenance](migration.md)
- [Validation evidence and limits](validation.md)
- [Installer progress and apt-cache investigation](installer-progress.md)
- [Setup and commands](../../README.md)

Durable authored notes live here. Local Graphify data is in `graphify-out/graph.json`, the audit report in `graphify-out/GRAPH_REPORT.md`, and the interactive view in `graphify-out/graph.html`. Open `graphify-out/obsidian/` as the Obsidian vault; authored notes are incorporated under `project-knowledge/`.

Use the installed Graphify skill for source-aware incremental updates. Query with `graphify query "your question"` and verify findings against source. Keep directed edges so caller/callee relationships remain meaningful. Regenerate the vault with `graphify export obsidian`, preserving authored notes. Exports and caches remain local and are excluded from Git and extraction.
