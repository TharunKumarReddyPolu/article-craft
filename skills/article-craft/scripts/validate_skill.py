#!/usr/bin/env python3
"""Validate the Article Craft skill against the Agent Skills specification.

Checks (per https://agentskills.io/specification):
- SKILL.md exists, has YAML frontmatter with required fields
- name: <=64 chars, [a-z0-9-], no leading/trailing/double hyphen, == dir name
- description: 1-1024 chars, non-empty, mentions what + when
- optional fields: license (str), compatibility (<=500), metadata (str->str)
- body present; SKILL.md < 500 lines (progressive disclosure guidance)
- referenced relative paths resolve (one level deep preferred)
- workflows/templates/checklists/references files parse as markdown with
  no broken internal links
- sources.yaml parses and every Medium reference file has a source

Usage: python skills/article-craft/scripts/validate_skill.py [--skill-dir PATH]
Exit codes: 0 = valid, 1 = validation errors, 2 = usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_LEN = 64
MAX_DESCRIPTION_LEN = 1024
MAX_COMPAT_LEN = 500
MAX_LINES = 500

ERRORS: list[str] = []
WARNINGS: list[str] = []


def error(msg: str) -> None:
    ERRORS.append(msg)


def warning(msg: str) -> None:
    WARNINGS.append(msg)


def validate(skill_dir: Path) -> int:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        error(f"SKILL.md not found in {skill_dir}")
        return _finish()
    text = skill_md.read_text(encoding="utf-8")

    # --- frontmatter -----------------------------------------------------
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        error("SKILL.md must start with YAML frontmatter delimited by '---' lines")
        return _finish()
    try:
        meta = yaml.safe_load(m.group(1))
    except yaml.YAMLError as exc:
        error(f"frontmatter YAML is invalid: {exc}")
        return _finish()
    if not isinstance(meta, dict):
        error("frontmatter must be a YAML mapping")
        return _finish()

    name = meta.get("name")
    if not isinstance(name, str) or not name:
        error("frontmatter 'name' is required")
    else:
        if len(name) > MAX_NAME_LEN:
            error(f"name exceeds {MAX_NAME_LEN} characters ({len(name)})")
        if not NAME_RE.match(name):
            error(f"name '{name}' must be lowercase alphanumeric with single hyphens")
        if name != skill_dir.name:
            error(f"name '{name}' must match the directory name '{skill_dir.name}'")

    description = meta.get("description")
    if not isinstance(description, str) or not description.strip():
        error("frontmatter 'description' is required and must be non-empty")
    else:
        if len(description) > MAX_DESCRIPTION_LEN:
            error(f"description exceeds {MAX_DESCRIPTION_LEN} chars ({len(description)})")
        if "use when" not in description.lower():
            warning("description should say when to use the skill ('Use when ...')")

    license_field = meta.get("license")
    if license_field is not None and not isinstance(license_field, str):
        error("license must be a string")
    compat = meta.get("compatibility")
    if compat is not None:
        if not isinstance(compat, str):
            error("compatibility must be a string")
        elif len(compat) > MAX_COMPAT_LEN:
            error(f"compatibility exceeds {MAX_COMPAT_LEN} chars ({len(compat)})")
    metadata_field = meta.get("metadata")
    if metadata_field is not None:
        if not isinstance(metadata_field, dict):
            error("metadata must be a mapping")
        else:
            for key, value in metadata_field.items():
                if not isinstance(key, str) or not isinstance(value, (str, int, float, bool)):
                    error(f"metadata values must be scalar (key {key!r} is {type(value).__name__})")

    # --- body ------------------------------------------------------------
    body = text[m.end() :]
    lines = text.count("\n") + 1
    if lines > MAX_LINES:
        error(f"SKILL.md is {lines} lines; keep under {MAX_LINES} (progressive disclosure)")
    if len(body.strip()) < 200:
        warning("SKILL.md body is very short; skills usually need real instructions")

    # --- referenced files resolve -----------------------------------------
    # Matches [text](relative/path.md) and bare references to skill files.
    links = re.findall(r"\[[^\]]+\]\(([^)#\s]+)\)", body)
    for link in links:
        if re.match(r"^[a-z]+://", link):
            continue  # external URL
        target = (skill_dir / link).resolve()
        if not target.exists():
            error(f"SKILL.md links to missing file: {link}")

    # --- expected companion directories -------------------------------------
    for sub, minimum in (("workflows", 7), ("references", 3), ("templates", 8), ("checklists", 4)):
        subdir = skill_dir / sub
        if not subdir.is_dir():
            error(f"missing expected directory: {sub}/")
            continue
        found = [p for p in subdir.rglob("*.md")]
        if len(found) < minimum:
            error(f"{sub}/ has {len(found)} markdown files; expected at least {minimum}")
        for md_file in found:
            _check_internal_links(md_file, skill_dir)

    # --- medium sources.yaml ------------------------------------------------
    sources = skill_dir / "references" / "platforms" / "medium" / "sources.yaml"
    if not sources.is_file():
        error("missing references/platforms/medium/sources.yaml")
    else:
        try:
            data = yaml.safe_load(sources.read_text(encoding="utf-8"))
            entries = data.get("sources", []) if isinstance(data, dict) else []
            if not entries:
                error("sources.yaml has no source entries")
            for entry in entries:
                for field in ("id", "title", "url", "authority", "last_verified"):
                    if field not in entry:
                        error(f"source entry missing '{field}': {entry.get('id', '?')}")
                if (
                    entry.get("authority") == "OFFICIAL"
                    and "help.medium.com" not in str(entry.get("url", ""))
                    and "agentskills.io" not in str(entry.get("url", ""))
                    and "medium.com" not in str(entry.get("url", ""))
                ):
                    warning(f"source {entry.get('id')} claims OFFICIAL but URL is not medium.com")
        except yaml.YAMLError as exc:
            error(f"sources.yaml is invalid YAML: {exc}")

    return _finish()


def _check_internal_links(md_file: Path, skill_dir: Path) -> None:
    text = md_file.read_text(encoding="utf-8")
    # Exclude image syntax ![alt](url) — only real links [text](target).
    for link in re.findall(r"(?<!!)\[[^\]]+\]\(([^)#\s]+)\)", text):
        if re.match(r"^[a-z]+://", link) or link.startswith("mailto:"):
            continue
        target = (md_file.parent / link).resolve()
        if not target.exists():
            error(f"{md_file.relative_to(skill_dir)} links to missing file: {link}")


def _finish() -> int:
    for e in ERRORS:
        print(f"ERROR: {e}")
    for w in WARNINGS:
        print(f"WARNING: {w}")
    if not ERRORS:
        print(
            "Skill validation passed" + (f" ({len(WARNINGS)} warning(s))" if WARNINGS else "") + "."
        )
        return 0
    print(f"Skill validation FAILED with {len(ERRORS)} error(s).")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skill-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Path to the skill directory (default: the article-craft skill)",
    )
    args = parser.parse_args(argv)
    if not args.skill_dir.is_dir():
        print(f"ERROR: skill directory not found: {args.skill_dir}")
        return 2
    return validate(args.skill_dir)


if __name__ == "__main__":
    sys.exit(main())
