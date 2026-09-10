"""Self-diagnosis: answer "why isn't this working?" before it's a support issue.

``article-craft doctor`` checks the real environment (Python version, PATH
resolution, workspace state, optional extras) and prints fixes, not verdicts.
Design rule: informational checks always pass; only resolvable-by-us problems
fail. Usage errors are the user's to fix; doctor makes them visible.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

from article_craft import __version__


@dataclass
class Diagnostic:
    """One check with a human fix, not a stack trace."""

    name: str
    ok: bool | None  # True / False / None = informational
    detail: str
    fix: str | None = None


@dataclass
class DoctorReport:
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def has_failures(self) -> bool:
        return any(d.ok is False for d in self.diagnostics)

    def as_text(self) -> str:
        lines = [f"article-craft {__version__} - environment doctor", ""]
        for d in self.diagnostics:
            if d.ok is True:
                mark = "[ ok ]"
            elif d.ok is False:
                mark = "[FAIL]"
            else:
                mark = "[info]"
            lines.append(f"{mark} {d.name}: {d.detail}")
            if d.fix:
                lines.append(f"       fix: {d.fix}")
        lines.append("")
        if self.has_failures:
            lines.append(
                "[FAIL] One or more checks failed. Apply the fixes above, then re-run `article-craft doctor`."
            )
            lines.append(
                "       Still stuck? Open an issue: "
                "https://github.com/TharunKumarReddyPolu/article-craft/issues"
            )
        else:
            lines.append(
                "[ ok ] Environment looks good. `article-craft demo` runs the 30-second tour."
            )
        return "\n".join(lines)


def run_doctor() -> DoctorReport:
    """Execute every diagnostic against the live environment."""
    report = DoctorReport()

    # --- Python version ---------------------------------------------------
    vi = sys.version_info
    if vi >= (3, 11):
        report.diagnostics.append(
            Diagnostic(
                "Python",
                True,
                f"{sys.version.split()[0]}",
                None,
            )
        )
    else:
        report.diagnostics.append(
            Diagnostic(
                "Python",
                False,
                f"{sys.version.split()[0]} (3.11+ required)",
                "Install Python 3.11+ from https://www.python.org/downloads/ "
                "or use `uv tool install article-craft`, which manages its own Python.",
            )
        )

    # --- CLI entry point resolves to the installed package -----------------
    import article_craft

    try:
        entry_ok = hasattr(article_craft, "__version__")
        installed_dist = None
        try:
            from importlib import metadata as importlib_metadata

            installed_dist = importlib_metadata.version("article-craft")
        except importlib_metadata.PackageNotFoundError:
            installed_dist = None

        if installed_dist is not None:
            report.diagnostics.append(
                Diagnostic(
                    "Package install",
                    True,
                    f"installed as a distribution (version {installed_dist})",
                    None,
                )
            )
            if installed_dist != __version__:
                report.diagnostics.append(
                    Diagnostic(
                        "Version mismatch",
                        False,
                        f"installed dist {installed_dist} != runtime {__version__}",
                        "Reinstall: uv tool install --force article-craft  (or pip install --force-reinstall article-craft)",
                    )
                )
        else:
            report.diagnostics.append(
                Diagnostic(
                    "Package install",
                    None,
                    "running from a source checkout (not pip-installed)",
                    "For the stable CLI: uv tool install article-craft",
                )
            )
        assert entry_ok  # __version__ import already proves this
    except Exception as exc:  # pragma: no cover - defensive
        report.diagnostics.append(
            Diagnostic("Package install", False, f"import failed: {exc}", None)
        )

    # --- Workspace ---------------------------------------------------------
    from article_craft.config import workspace_dir

    ws = workspace_dir()
    cfg = ws / "config.yaml"
    if cfg.exists():
        report.diagnostics.append(Diagnostic("Workspace", True, f"found {ws}/", None))
    else:
        report.diagnostics.append(
            Diagnostic(
                "Workspace",
                None,
                "not initialized yet",
                "Run: article-craft init",
            )
        )

    # --- Voice profile ------------------------------------------------------
    voice = ws / "voice.md"
    if voice.exists():
        report.diagnostics.append(Diagnostic("Voice profile", True, f"found {voice}", None))
    else:
        report.diagnostics.append(
            Diagnostic(
                "Voice profile",
                None,
                "not built yet (reviews use generic style heuristics)",
                "Run: article-craft learn ./your-old-articles/",
            )
        )

    # --- MCP optional extra -------------------------------------------------
    try:
        import mcp  # noqa: F401

        report.diagnostics.append(
            Diagnostic("MCP server (optional)", True, "mcp SDK importable", None)
        )
    except ImportError:
        report.diagnostics.append(
            Diagnostic(
                "MCP server (optional)",
                None,
                "not installed",
                "pip install 'article-craft[mcp]'  →  adds `article-craft-mcp` for MCP-capable agents",
            )
        )

    # --- uv availability (nice for contributors) ----------------------------
    import shutil

    uv_path = shutil.which("uv")
    if uv_path:
        report.diagnostics.append(
            Diagnostic("uv (dev convenience)", True, f"found at {uv_path}", None)
        )
    else:
        report.diagnostics.append(
            Diagnostic(
                "uv (dev convenience)",
                None,
                "not found",
                "Optional; contributors: https://docs.astral.sh/uv/getting-started/installation/",
            )
        )

    return report
