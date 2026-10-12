"""Pin the skill's version to the article-craft package version.

The Agent Skill header in SKILL.md drifted to 2.0.0 while the package was
2.2.0. validate_skill.py now catches that in CI; this test makes the same
check visible in plain pytest so `python -m pytest` alone fails loudly.
"""

from __future__ import annotations

import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2] / "skills" / "article-craft"
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import validate_skill as vs  # noqa: E402


def test_skill_version_matches_package() -> None:
    """SKILL.md metadata.version and pyproject [project].version agree."""
    trailing = vs.validate(SKILL_DIR)
    # The validator exits 0 only when metadata.version == package version
    # (or is absent entirely) among its other checks.
    assert trailing == 0, "skill validation failed (see stderr for reasons)"

    import re

    skill_md = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r'version:\s*"?(\d+\.\d+\.\d+)"?', skill_md)
    assert m, "SKILL.md frontmatter has no version line"

    pkg_version = vs._package_version(SKILL_DIR)
    assert pkg_version is not None, (
        "package version undetectable; the check above cannot be trusted"
    )
    assert m.group(1) == pkg_version, (
        f"SKILL.md version {m.group(1)} != package version {pkg_version} - "
        "bump both together at release time"
    )
