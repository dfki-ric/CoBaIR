"""Rewrite a README badge block from environment variables.

`update_badges.py quality` writes the ruff and docstring badges (LINT, DOCS, BADGE_LINK) between
`<!-- badges:start/end -->`, `update_badges.py coverage` the test coverage badge (COVERAGE,
BADGE_LINK) between `<!-- coverage-badge:start/end -->`. The Quality and the CI workflow each
rewrite only their own block, so they don't overwrite each other's numbers.
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import quote

README = Path("README.md")


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


def percent_color(pct: float) -> str:
    """Map a coverage (docstrings or tests) to a badge color.

    Args:
        pct: The coverage in percent.

    Returns:
        The shields.io color name.
    """
    for threshold, color in ((90, "brightgreen"), (75, "green"), (60, "yellow"), (50, "orange")):
        if pct >= threshold:
            return color
    return "red"


def badges(lint: int, docs: float, link: str) -> str:
    """Return the markdown of the quality badges.

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
        shield("Docstring coverage", f"{docs:g}%", percent_color(docs), link),
    ])


def coverage_badge(coverage: float, link: str) -> str:
    """Return the markdown of the test coverage badge.

    Args:
        coverage: Test coverage of the cobair package in percent.
        link: URL the badge links to.

    Returns:
        The badge.
    """
    return shield("Test coverage", f"{coverage:g}%", percent_color(coverage), link)


def replace_block(text: str, block: str, name: str = "badges") -> str:
    """Replace the content between the markers `<!-- name:start -->` and `<!-- name:end -->`.

    Args:
        text: The README content.
        block: The new content between the markers.
        name: The name of the markers.

    Returns:
        The README content with the new block.

    Raises:
        SystemExit: If the README has no such markers.
    """
    pattern = re.compile(rf"(<!-- {name}:start -->\n).*?(<!-- {name}:end -->)", re.DOTALL)
    if not pattern.search(text):
        raise SystemExit(f"README.md is missing the <!-- {name}:start/end --> markers")
    return pattern.sub(lambda m: f"{m[1]}{block}\n{m[2]}", text, count=1)


def main(argv: list = None) -> None:
    """Replace the content of one badge block in README.md.

    Args:
        argv: `["quality"]` or `["coverage"]`, defaults to the command line arguments.

    Raises:
        SystemExit: If the argument is neither quality nor coverage.
    """
    argv = sys.argv[1:] if argv is None else argv
    env = os.environ
    if argv == ["quality"]:
        name, block = "badges", badges(int(env["LINT"]), float(env["DOCS"]), env["BADGE_LINK"])
    elif argv == ["coverage"]:
        name, block = "coverage-badge", coverage_badge(float(env["COVERAGE"]), env["BADGE_LINK"])
    else:
        raise SystemExit("usage: update_badges.py quality|coverage")
    README.write_text(replace_block(README.read_text(encoding="utf-8"), block, name),
                      encoding="utf-8")


if __name__ == "__main__":
    main()
