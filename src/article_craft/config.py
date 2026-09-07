"""Per-writer workspace configuration (``.article-craft/``).

Personal preferences live in the workspace, never in the skill: the global
skill stays neutral. Nothing here is hardcoded opinion — every field is a
user choice with an honest default.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class StyleConfig(BaseModel):
    tone: str = "conversational-technical"
    technical_depth: str = "intermediate"
    use_first_person: bool = True
    avoid_clickbait: bool = True


class PreferencesConfig(BaseModel):
    avoid_em_dash: bool = False
    paragraph_style: str = "medium"  # short | medium | long
    excessive_headings: bool = False


class PlatformConfig(BaseModel):
    default: str = "medium"  # medium | generic (V1)


class AuthorConfig(BaseModel):
    name: str | None = None
    topics: list[str] = Field(default_factory=list)
    experience: str = "intermediate"


class WorkspaceConfig(BaseModel):
    """Root of .article-craft/config.yaml."""

    version: int = 1
    author: AuthorConfig = Field(default_factory=AuthorConfig)
    audience: str = "software-engineers"
    style: StyleConfig = Field(default_factory=StyleConfig)
    preferences: PreferencesConfig = Field(default_factory=PreferencesConfig)
    platform: PlatformConfig = Field(default_factory=PlatformConfig)


WORKSPACE_DIR = ".article-craft"

DEFAULT_CONFIG_YAML = """\
# Article Craft workspace configuration.
# Personal to you — never shipped with the skill. Edit freely.

version: 1

author:
  # name: Your Name
  topics: []
  experience: intermediate

audience: software-engineers

style:
  tone: conversational-technical
  technical_depth: intermediate
  use_first_person: true
  avoid_clickbait: true

preferences:
  avoid_em_dash: false
  paragraph_style: medium
  excessive_headings: false

platform:
  default: medium   # medium | generic (V1)
"""

AUDIENCE_MD = """\
# Audience

<!-- Who do you write for? Be specific: role, experience level, what they
want. This file is advisory context for every Article Craft workflow. -->

- Primary audience: software engineers
- Experience level: intermediate
- What they want from your articles:
"""

TOPICS_MD = """\
# Topics

<!-- What do you write about? Your real areas of experience — the tool
uses this to keep advice grounded in what you actually know. -->

-
"""

PREFERENCES_MD = """\
# Preferences

<!-- Editing preferences the agent should honor in every workflow. Examples:

- Use sentence-case headings
- Prefer "use" over "utilize"
- No em dashes
- Code samples in python with expected output
-->

-
"""


def workspace_dir(base: Path | None = None) -> Path:
    return (base or Path.cwd()) / WORKSPACE_DIR


def load_config(base: Path | None = None) -> WorkspaceConfig:
    """Load .article-craft/config.yaml, or defaults if absent. Malformed
    config raises with an actionable message."""
    path = workspace_dir(base) / "config.yaml"
    if not path.exists():
        return WorkspaceConfig()
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ValueError(
            f"Could not parse {path}: {exc}. Fix the YAML and retry, or delete "
            "the file to fall back to defaults."
        ) from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping.")
    return WorkspaceConfig(**data)


def save_config(config: WorkspaceConfig, base: Path | None = None) -> Path:
    directory = workspace_dir(base)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "config.yaml"
    path.write_text(yaml.safe_dump(config.model_dump(), sort_keys=False), encoding="utf-8")
    return path


def init_workspace(
    base: Path | None = None,
    *,
    defaults: bool = False,
    answers: dict | None = None,
) -> tuple[Path, list[str]]:
    """Create .article-craft/ with config + advisory files.

    Returns (workspace_path, created_files). If a workspace already exists,
    existing files are preserved and only missing ones are created.
    """
    directory = workspace_dir(base)
    directory.mkdir(parents=True, exist_ok=True)
    created: list[str] = []

    config_path = directory / "config.yaml"
    if config_path.exists():
        config = load_config(base)
    else:
        config = WorkspaceConfig()
        if answers:
            for key, value in answers.items():
                if key in ("audience", "experience") and value:
                    if key == "audience":
                        config.audience = str(value)
                    else:
                        config.author.experience = str(value)
                elif key == "topics" and value:
                    config.author.topics = [t.strip() for t in str(value).split(",") if t.strip()]
                elif key == "tone" and value:
                    config.style.tone = str(value)
                elif key == "technical_depth" and value:
                    config.style.technical_depth = str(value)
                elif key == "use_first_person" and value is not None:
                    config.style.use_first_person = bool(value)
                elif key == "platform" and value:
                    config.platform.default = str(value)
        config_path.write_text(DEFAULT_CONFIG_YAML, encoding="utf-8")
        created.append("config.yaml")

    files: dict[str, str] = {
        "voice.md": "# Writing Voice Profile\n\n_No profile yet. Run "
        "`article-craft learn ./my-articles/` to build one from "
        "your existing articles._\n",
        "audience.md": AUDIENCE_MD,
        "topics.md": TOPICS_MD,
        "preferences.md": PREFERENCES_MD,
    }
    if defaults:
        # Fill advisory files with defaults only when creating fresh.
        for name in ("audience.md", "topics.md", "preferences.md"):
            target = directory / name
            if not target.exists() and answers:
                filled = _fill_with_answers(name, answers)
                if filled:
                    files[name] = filled
    for name, content in files.items():
        target = directory / name
        if not target.exists():
            target.write_text(content, encoding="utf-8")
            created.append(name)
    return directory, created


def _fill_with_answers(name: str, answers: dict) -> str | None:
    if name == "audience.md" and answers.get("audience"):
        return AUDIENCE_MD.replace("software engineers", str(answers["audience"]))
    if name == "topics.md" and answers.get("topics"):
        topics = "\n".join(f"- {t.strip()}" for t in str(answers["topics"]).split(",") if t.strip())
        return TOPICS_MD.replace("-\n", topics + "\n")
    if name == "preferences.md" and answers.get("avoid"):
        return PREFERENCES_MD.replace("-\n", f"- Avoid: {answers['avoid']}\n")
    return None
