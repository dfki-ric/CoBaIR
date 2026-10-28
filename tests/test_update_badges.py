"""Tests for .github/scripts/update_badges.py."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "update_badges.py"
spec = importlib.util.spec_from_file_location("update_badges", SCRIPT)
update_badges = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update_badges)

LINK = "https://example.com/quality"


def test_shield_escapes_label_and_message():
    """Dashes, underscores and spaces are escaped for shields.io."""
    badge = update_badges.shield("a-b c_d", "94.5%", "green", LINK)
    assert badge == f"[![a-b c_d](https://img.shields.io/badge/a--b%20c__d-94.5%25-green)]({LINK})"


@pytest.mark.parametrize("pct, color", [
    (100, "brightgreen"), (90, "brightgreen"), (89.9, "green"), (75, "green"),
    (60, "yellow"), (50, "orange"), (49.9, "red"), (0, "red"),
])
def test_docs_color(pct, color):
    """Docstring coverage maps to the expected color."""
    assert update_badges.docs_color(pct) == color


def test_badges_lint_passing_and_issues():
    """Zero ruff issues show as passing, others as a count."""
    assert "passing-brightgreen" in update_badges.badges(0, 100.0, LINK)
    block = update_badges.badges(779, 94.5, LINK)
    assert "779%20issues-yellow" in block
    assert "94.5%25-brightgreen" in block
    assert len(block.splitlines()) == 2


def test_replace_block_keeps_surrounding_text():
    """Only the content between the markers is replaced."""
    text = "# Title\n<!-- badges:start -->\nold\nlines\n<!-- badges:end -->\nrest\n"
    assert update_badges.replace_block(text, "new") == \
        "# Title\n<!-- badges:start -->\nnew\n<!-- badges:end -->\nrest\n"


def test_replace_block_without_markers():
    """A README without markers is an error."""
    with pytest.raises(SystemExit):
        update_badges.replace_block("# Title\n", "new")


def test_main_rewrites_readme(tmp_path, monkeypatch):
    """main() reads the environment and rewrites README.md in the working directory."""
    readme = tmp_path / "README.md"
    readme.write_text("<!-- badges:start -->\n<!-- badges:end -->\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LINT", "3")
    monkeypatch.setenv("DOCS", "80")
    monkeypatch.setenv("BADGE_LINK", LINK)
    update_badges.main()
    text = readme.read_text(encoding="utf-8")
    assert "3%20issues-yellow" in text
    assert "80%25-green" in text
