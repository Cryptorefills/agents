#!/usr/bin/env python3
"""Generate the Agent Skills discovery index and sync SKILL.md files into cryptorefills-api.

Walks every ``skills/<name>/SKILL.md`` in this repository, computes its SHA-256,
extracts the description from YAML frontmatter, renders an RFC v0.2.0 discovery
index, and writes it — along with byte-for-byte copies of each SKILL.md — into
the target cryptorefills-api checkout.

Intended to run inside the ``Publish Agent Skills`` GitHub Actions workflow, but
safe to run locally for dry-runs:

    python .github/scripts/generate-agent-skills-index.py \\
        --agents-dir . \\
        --api-dir ../cryptorefills-api
"""

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import sys

import yaml

SCHEMA_URL = "https://schemas.agentskills.io/discovery/0.2.0/schema.json"
URL_TEMPLATE = "/.well-known/agent-skills/{name}/SKILL.md"

FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(content: str) -> dict:
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        raise ValueError("SKILL.md missing YAML frontmatter")
    parsed = yaml.safe_load(match.group(1)) or {}
    if not isinstance(parsed, dict):
        raise ValueError("YAML frontmatter did not parse to a mapping")
    return parsed


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_entry(skill_dir: pathlib.Path) -> tuple[dict, bytes]:
    name = skill_dir.name
    src = skill_dir / "SKILL.md"
    if not src.is_file():
        raise FileNotFoundError(f"{name}: SKILL.md missing at {src}")

    data = src.read_bytes()
    frontmatter = parse_frontmatter(data.decode("utf-8"))

    declared = str(frontmatter.get("name", "")).strip()
    if declared and declared != name:
        print(
            f"[warn] {name}: frontmatter name '{declared}' differs from directory name",
            file=sys.stderr,
        )

    description = str(frontmatter.get("description", "")).strip()
    if not description:
        raise ValueError(f"{name}: description missing or empty in frontmatter")
    if len(description) > 1024:
        raise ValueError(f"{name}: description exceeds RFC v0.2.0 limit of 1024 chars")

    entry = {
        "name": name,
        "type": "skill-md",
        "description": description,
        "url": URL_TEMPLATE.format(name=name),
        "digest": f"sha256:{sha256_hex(data)}",
    }
    return entry, data


def write_output(api_dir: pathlib.Path, entries: list[dict], payloads: dict[str, bytes]) -> None:
    conf = api_dir / "conf"
    index_path = conf / "agent-skills-index.json"
    skills_root = conf / "agent-skills"

    if not conf.is_dir():
        raise FileNotFoundError(f"cryptorefills-api conf/ not found: {conf}")

    # Rebuild skills directory from scratch so upstream deletions propagate.
    if skills_root.exists():
        shutil.rmtree(skills_root)
    skills_root.mkdir()

    for name, data in payloads.items():
        dest = skills_root / name / "SKILL.md"
        dest.parent.mkdir()
        dest.write_bytes(data)

    index = {"$schema": SCHEMA_URL, "skills": entries}
    index_path.write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agents-dir", required=True, type=pathlib.Path)
    parser.add_argument("--api-dir", required=True, type=pathlib.Path)
    args = parser.parse_args()

    skills_root = args.agents_dir / "skills"
    if not skills_root.is_dir():
        print(f"[fail] skills directory missing: {skills_root}", file=sys.stderr)
        return 1

    skill_dirs = sorted(d for d in skills_root.iterdir() if d.is_dir())
    if not skill_dirs:
        print(f"[fail] no skill subdirectories under {skills_root}", file=sys.stderr)
        return 1

    entries: list[dict] = []
    payloads: dict[str, bytes] = {}
    for skill_dir in skill_dirs:
        entry, data = build_entry(skill_dir)
        entries.append(entry)
        payloads[entry["name"]] = data
        print(f"[ok] {entry['name']}: {entry['digest']}")

    write_output(args.api_dir, entries, payloads)
    print(f"[ok] wrote {len(entries)} skill(s) into {args.api_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
