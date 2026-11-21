#!/usr/bin/env python3
"""Check documentation commands and repository links without executing examples."""
from pathlib import Path
import re
import subprocess


def anchors(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    result = set()
    for heading in re.findall(r"^#{1,6} (.+)$", text, re.M):
        heading = re.sub(r"[`*]", "", heading).lower()
        slug = "".join(c for c in heading if c.isalnum() or c in " -_").replace(" ", "-")
        result.add(slug)
    return result


def main():
    root = Path(__file__).resolve().parents[2]
    paths = [root / name for name in ["README.md", "TEMPLATE.md", "AGENTS.md"]]
    paths += sorted((root / "docs").rglob("*.md"))
    blocks = links = 0
    for path in paths:
        text = path.read_text()
        for block in re.findall(r"```bash\n(.*?)```", text, re.S):
            result = subprocess.run(["bash", "-n"], input=block, text=True, capture_output=True)
            if result.returncode:
                raise SystemExit(f"{path.relative_to(root)}: invalid Bash example\n{result.stderr}")
            blocks += 1
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if target.startswith(("https:", "http:", "mailto:")):
                continue
            file, _, anchor = target.partition("#")
            dest = path.parent / file if file else path
            if not dest.exists():
                raise SystemExit(f"{path.relative_to(root)}: missing link {target}")
            if anchor and dest.suffix == ".md" and anchor not in anchors(dest.read_text()):
                raise SystemExit(f"{path.relative_to(root)}: missing heading {target}")
            links += 1
    print(f"Documentation: {blocks} Bash examples and {links} local links passed")


if __name__ == "__main__":
    main()
