#!/usr/bin/env python3
"""Validate the repository-root Codex Skill and its local references."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"


def main() -> None:
    source = SKILL.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", source, re.DOTALL)
    if not match:
        raise SystemExit("SKILL.md 缺少有效 YAML frontmatter")
    metadata = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            metadata[key.strip()] = value.strip().strip('"\'')
    if metadata.get("name") != "moxing-studio":
        raise SystemExit("Skill name 必须为 moxing-studio")
    if not isinstance(metadata.get("description"), str) or len(metadata["description"].strip()) < 20:
        raise SystemExit("Skill description 缺失或过短")
    references = sorted(set(re.findall(r"\]\((references/[^)#]+)", source)))
    missing = [reference for reference in references if not (ROOT / reference).is_file()]
    if missing:
        raise SystemExit(f"缺少引用文件：{', '.join(missing)}")
    if re.search(r"\b(?:TODO|TBD|PLACEHOLDER)\b", source, re.IGNORECASE):
        raise SystemExit("SKILL.md 含未完成占位符")
    print(f"skill=valid name={metadata['name']} references={len(references)}")


if __name__ == "__main__":
    main()
