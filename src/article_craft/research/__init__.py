"""Research: claim extraction, fact-check scaffolding, research artifacts."""

from article_craft.research.artifact import render_research_doc
from article_craft.research.claims import extract_claims, scaffold_factcheck

__all__ = ["extract_claims", "render_research_doc", "scaffold_factcheck"]
