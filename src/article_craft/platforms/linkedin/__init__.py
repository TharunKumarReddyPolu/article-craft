"""LinkedIn adapter package."""

from article_craft.platforms.linkedin.adapter import (
    LinkedInAdapter,
    linkedin_pre_publish_check,
)

__all__ = ["LinkedInAdapter", "linkedin_pre_publish_check"]
