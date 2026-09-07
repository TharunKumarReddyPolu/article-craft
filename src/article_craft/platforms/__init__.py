"""Platform adapters. The core never imports one directly; resolve by id."""

from article_craft.platforms.base import (
    PlatformAdapter,
    available_platforms,
    get_adapter,
    register_adapter,
)

__all__ = [
    "PlatformAdapter",
    "available_platforms",
    "get_adapter",
    "register_adapter",
]


def load_builtin_adapters() -> None:
    """Import built-in adapters so they register themselves. Safe to call
    multiple times."""
    from article_craft.platforms.devto import adapter as _devto  # noqa: F401
    from article_craft.platforms.hashnode import adapter as _hashnode  # noqa: F401
    from article_craft.platforms.linkedin import adapter as _linkedin  # noqa: F401
    from article_craft.platforms.medium import adapter as _medium  # noqa: F401
    from article_craft.platforms.substack import adapter as _substack  # noqa: F401


load_builtin_adapters()
