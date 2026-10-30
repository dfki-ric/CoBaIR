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
def test_percent_color(pct, color):
    """A coverage maps to the expected color."""
    assert update_badges.percent_color(pct) == color


def test_badges_lint_passing_and_issues():
    """Zero ruff issues show as passing, others as a count."""
    assert "passing-brightgreen" in update_badges.badges(0, 100.0, LINK)
    block = update_badges.badges(779, 94.5, LINK)
    assert "779%20issues-yellow" in block
    assert "94.5%25-brightgreen" in block
    assert len(block.splitlines()) == 2


def test_coverage_badge():
    """The test coverage badge shows the percentage with its color."""
    assert "Test%20coverage-72.3%25-yellow" in update_badges.coverage_badge(72.3, LINK)


def test_replace_block_keeps_surrounding_text():
    """Only the content between the markers is replaced."""
    text = "# Title\n<!-- badges:start -->\nold\nlines\n<!-- badges:end -->\nrest\n"
    assert update_badges.replace_block(text, "new") == \
        "# Title\n<!-- badges:start -->\nnew\n<!-- badges:end -->\nrest\n"


def test_replace_block_without_markers():
    """A README without markers is an error."""
    with pytest.raises(SystemExit):
        update_badges.replace_block("# Title\n", "new")
    with pytest.raises(SystemExit):
        update_badges.replace_block("<!-- badges:start -->\n<!-- badges:end -->\n", "new",
                                    "coverage-badge")


README = ("<!-- badges:start -->\nold quality\n<!-- badges:end -->\n"
          "<!-- coverage-badge:start -->\nold coverage\n<!-- coverage-badge:end -->\n")


def test_main_quality_rewrites_only_its_block(tmp_path, monkeypatch):
    """`quality` reads LINT and DOCS and leaves the coverage badge alone."""
    readme = tmp_path / "README.md"
    readme.write_text(README, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LINT", "3")
    monkeypatch.setenv("DOCS", "80")
    monkeypatch.setenv("BADGE_LINK", LINK)
    update_badges.main(["quality"])
    text = readme.read_text(encoding="utf-8")
    assert "3%20issues-yellow" in text and "80%25-green" in text
    assert "old coverage" in text and "old quality" not in text


def test_main_coverage_rewrites_only_its_block(tmp_path, monkeypatch):
    """`coverage` reads COVERAGE and leaves the quality badges alone."""
    readme = tmp_path / "README.md"
    readme.write_text(README, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COVERAGE", "91.2")
    monkeypatch.setenv("BADGE_LINK", LINK)
    update_badges.main(["coverage"])
    text = readme.read_text(encoding="utf-8")
    assert "Test%20coverage-91.2%25-brightgreen" in text
    assert "old quality" in text and "old coverage" not in text


def test_main_needs_a_mode():
    """Without quality or coverage the script stops."""
    with pytest.raises(SystemExit):
        update_badges.main([])
