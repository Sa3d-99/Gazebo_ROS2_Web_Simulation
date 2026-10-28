# Project knowledge

Read [docs/knowledge-base/README.md](docs/knowledge-base/README.md) before substantial investigation or implementation. It links architecture, compatibility decisions, provenance, and validation evidence.

- Graphify graph: `graphify-out/graph.json`; report: `graphify-out/GRAPH_REPORT.md`.
- Local Obsidian vault: `graphify-out/obsidian/`; interactive graph: `graphify-out/graph.html`.
- Use `/home/sa3d/.codex/skills/graphify/SKILL.md` and `/home/sa3d/.local/bin/graphify` for graph queries, builds, and source-aware incremental updates. Verify significant findings against current source.
- Generated graph/cache/vault outputs are local and ignored by Git. Exclude generated files, dependencies, build output, and secrets using `.graphifyignore`.
- Keep durable notes in `docs/knowledge-base/`, preserve authored notes on export, and incorporate them into the vault. The standing workflow authorizes Obsidian export.

This is the standalone Gazebo project. It runs only Ubuntu 22.04 / ROS Humble / Fortress or Ubuntu 24.04 / ROS Jazzy / Harmonic. Do not introduce Isaac launch or shutdown behavior. Distinguish inherited integration evidence from new standalone validation.
