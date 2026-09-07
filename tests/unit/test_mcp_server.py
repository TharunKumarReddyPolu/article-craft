"""Tests for the MCP server (in-process client; requires the mcp extra)."""

from __future__ import annotations

import pytest

pytest.importorskip("mcp", reason="MCP extra not installed (article-craft[mcp])")

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ARTICLE = """---
title: How I bounded our Kafka fan-out
topics: [kafka, backend]
canonical_url: "https://blog.example.com/kafka-fanout"
ai_assistance: none
---

# How I bounded our Kafka fan-out

Last Black Friday our consumer fell seven hours behind. I owned the fix.

## What broke

One hot user generated 50,000 notifications. I benchmarked the fix: p99
went from 2.3s to 180ms.

## What I changed

We bounded fan-out per partition key, which preserved ordering.
"""


def _write_article(tmp_path) -> str:
    path = tmp_path / "article.md"
    path.write_text(ARTICLE, encoding="utf-8")
    return str(path)


async def _list_tools(server_path: str) -> list[str]:
    params = StdioServerParameters(command="article-craft-mcp")
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
        return [tool.name for tool in tools.tools]


def _tool_names(mcp) -> list[str]:
    import asyncio
    import inspect

    listed = mcp.list_tools()
    if inspect.iscoroutine(listed):
        listed = asyncio.run(listed)
    return [tool.name for tool in listed]


def test_server_defines_expected_tools() -> None:
    from article_craft.mcp import server

    tools = set(_tool_names(server.mcp))

    assert {
        "review_article",
        "platform_check",
        "factcheck_scaffold",
        "check_images",
        "adapt_social_post",
        "export_prep",
        "supported_platforms",
    } <= tools


def _call(tool, *args, **kwargs):
    """Call an MCP-registered tool function directly (1.x wraps as .fn)."""
    fn = getattr(tool, "fn", tool)
    return fn(*args, **kwargs)


def test_tools_run_against_real_article(tmp_path) -> None:
    from article_craft.mcp import server

    path = _write_article(tmp_path)
    review = _call(server.review_article, path, platform="devto")
    assert "Editorial Review" in review
    check = _call(server.platform_check, path, platform="devto")
    assert "DEVTO PRE-PUBLISH CHECK" in check.upper()
    scaffold = _call(server.factcheck_scaffold, path)
    assert "Claim" in scaffold or "claim" in scaffold
    images = _call(server.check_images, path)
    assert "Images" in images
    post = _call(server.adapt_social_post, path, platform="linkedin")
    assert "From my article" in post
    platforms = _call(server.supported_platforms)
    assert "devto" in platforms


def test_export_prep_writes_file(tmp_path) -> None:
    from article_craft.mcp import server

    path = _write_article(tmp_path)
    out = tmp_path / "exports"
    report = _call(server.export_prep, path, platform="devto", out_dir=str(out))
    assert "Export prep" in report
    assert any(out.glob("*.md"))


def test_unknown_platform_raises_valueerror(tmp_path) -> None:
    from article_craft.mcp import server

    path = _write_article(tmp_path)
    try:
        _call(server.platform_check, path, platform="twitter")
    except ValueError as exc:
        assert "Unknown platform" in str(exc)
    else:
        raise AssertionError("expected ValueError")
