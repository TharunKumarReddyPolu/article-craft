# MCP Server

Article Craft ships an optional **MCP server** that exposes its deterministic
editorial engines as tools, so any MCP-capable agent can call them directly —
no CLI wrapping required.

## Install

```bash
pip install "article-craft[mcp]"
```

## Run

```bash
article-craft-mcp
```

The server uses the **stdio transport** — it is meant to be spawned by your
agent, not run interactively.

## Register with your agent

**Claude Code:**

```bash
claude mcp add article-craft -- article-craft-mcp
```

**Claude Desktop / other MCP clients** — add to your MCP config:

```json
{
  "mcpServers": {
    "article-craft": {
      "command": "article-craft-mcp"
    }
  }
}
```

## Tools

| Tool | What it does |
|---|---|
| `review_article` | Full editorial review: 8-dimension reasoned score, critical issues, platform-compatibility notes |
| `platform_check` | Policy-grounded check against `medium`, `devto`, `hashnode`, `substack`, or `linkedin` |
| `extract_claims` | Deterministic claim extraction with classification hints (no verification — see below) |
| `check_images` | Image and alt-text audit of a markdown article |
| `analyze_title` | Title analysis: clickbait, keyword stuffing, length, promise clarity |
| `build_outline` | Editorial outline for an idea, audience, and article type |
| `export_article` | Write platform-ready files locally (zero network) |

## Design guarantees

- **No LLM inside.** The server runs the same deterministic engines as the
  CLI. Judgment stays with your agent; the server supplies evidence.
- **No network calls.** Nothing is fetched, nothing is uploaded. Claim
  *verification* is not an MCP tool — that requires your agent's web access
  under your direction, and pretending otherwise would be dishonest.
- **No publishing.** `export_article` writes files locally. Nothing is ever
  posted to a platform.
- **Same honesty guards.** Platform checks cite source ids from the
  per-platform `sources.yaml`; the shared base raises if one is missing.

## Verifying it works

```bash
# initialize handshake + tools/list over stdio
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke","version":"0.0.0"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | article-craft-mcp
```

You should see a JSON-RPC response listing the seven tools. The test suite
(`tests/unit/test_mcp_server.py`) runs this handshake in-process.
