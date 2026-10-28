"""Rewrite the README badge block from the LINT, DOCS and BADGE_LINK environment variables."""

import os
import re
from pathlib import Path
from urllib.parse import quote

README = Path("README.md")
BLOCK = re.compile(r"(<!-- badges:start -->\n).*?(<!-- badges:end -->)", re.DOTALL)


def shield(label: str, message: str, color: str, link: str) -> str:
    """Return a markdown image link to a static shields.io badge.

    Args:
        label: Left part of the badge.
        message: Right part of the badge.
        color: shields.io color name.
        link: URL the badge links to.

    Returns:
        The markdown for the badge.
    """
    def esc(s: str) -> str:
        return quote(s.replace("-", "--").replace("_", "__"))

    return f"[![{label}](https://img.shields.io/badge/{esc(label)}-{esc(message)}-{color})]({link})"


def docs_color(pct: float) -> str:
    """Map docstring coverage to a badge color.

    Args:
        pct: Docstring coverage in percent.

    Returns:
        The shields.io color name.
    """
    for threshold, color in ((90, "brightgreen"), (75, "green"), (60, "yellow"), (50, "orange")):
        if pct >= threshold:
            return color
    return "red"


def badges(lint: int, docs: float, link: str) -> str:
    """Return the markdown of all quality badges.

    Args:
        lint: Number of ruff issues.
        docs: Docstring coverage in percent.
        link: URL the badges link to.

    Returns:
        One badge per line.
    """
    return "\n".join([
        shield("Ruff linting issues", "passing" if lint == 0 else f"{lint} issues",
               "brightgreen" if lint == 0 else "yellow", link),
        shield("Docstring coverage", f"{docs:g}%", docs_color(docs), link),
    ])


def replace_block(text: str, block: str) -> str:
    """Replace the content between the badge markers.

    Args:
        text: The README content.
        block: The new content between the markers.

    Returns:
        The README content with the new badge block.

    Raises:
        SystemExit: If the README has no badge markers.
    """
    if not BLOCK.search(text):
        raise SystemExit("README.md is missing the <!-- badges:start/end --> markers")
    return BLOCK.sub(lambda m: f"{m[1]}{block}\n{m[2]}", text, count=1)


def main() -> None:
    """Replace the content between the badge markers in README.md."""
    block = badges(int(os.environ["LINT"]), float(os.environ["DOCS"]), os.environ["BADGE_LINK"])
    README.write_text(replace_block(README.read_text(encoding="utf-8"), block), encoding="utf-8")


if __name__ == "__main__":
    main()
