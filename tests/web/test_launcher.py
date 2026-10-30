"""Tests for the automatic frontend rebuild of `cobair-web` in a source checkout."""

# System imports
import subprocess

# 3rd party imports
import pytest

pytest.importorskip('reflex')

# local imports
from cobair.web import build, launcher  # noqa: E402

# end file header
__author__ = 'Adrian Lubitz'


@pytest.fixture
def project(tmp_path):
    """A Reflex project directory with sources, build output and caches.

    Returns:
        Path: The project directory.
    """
    (tmp_path / 'app.py').write_text('APP = 1\n')
    (tmp_path / 'launcher.py').write_text('LAUNCHER = 1\n')
    (tmp_path / 'assets' / 'external').mkdir(parents=True)
    (tmp_path / 'assets' / 'logo.png').write_bytes(b'logo')
    (tmp_path / 'assets' / 'external' / 'generated.js').write_text('x = 1')
    (tmp_path / 'examples').mkdir()
    (tmp_path / 'examples' / 'example.yml').write_text('contexts: {}\n')
    for generated in ('frontend', '.web', '__pycache__'):
        (tmp_path / generated).mkdir()
        (tmp_path / generated / 'generated.py').write_text('X = 1\n')
    return tmp_path


@pytest.mark.parametrize('source', ['app.py', 'assets/logo.png'])
def test_source_hash_changes_with_the_sources(project, source):
    """Editing a module or an asset of the frontend changes the hash."""
    before = build.source_hash(project)
    (project / source).write_text('changed\n')
    assert build.source_hash(project) != before


def test_source_hash_ignores_build_output_and_launcher(project):
    """Build output, caches and modules that are not compiled into the frontend don't count."""
    before = build.source_hash(project)
    (project / 'launcher.py').write_text('LAUNCHER = 2\n')
    (project / 'assets' / 'external' / 'generated.js').write_text('x = 2')
    (project / 'examples' / 'example.yml').write_text('contexts: {a: {b: 1}}\n')
    for generated in ('frontend', '.web', '__pycache__'):
        (project / generated / 'generated.py').write_text('X = 2\n')
    assert build.source_hash(project) == before


def test_is_up_to_date(tmp_path, monkeypatch):
    """The frontend is up to date only if it exists and its stamp matches the sources."""
    frontend = tmp_path / 'frontend'
    monkeypatch.setattr(build, 'FRONTEND_DIR', frontend)
    monkeypatch.setattr(build, 'STAMP_FILE', frontend / 'build-hash.txt')
    monkeypatch.setattr(build, 'source_hash', lambda: 'abc')
    assert not build.is_up_to_date()
    frontend.mkdir()
    (frontend / 'index.html').write_text('')
    assert not build.is_up_to_date()  # built before the stamp existed
    (frontend / 'build-hash.txt').write_text('old\n')
    assert not build.is_up_to_date()
    (frontend / 'build-hash.txt').write_text('abc\n')
    assert build.is_up_to_date()


@pytest.mark.parametrize('checkout, up_to_date, rebuilt', [
    (True, False, True),
    (True, True, False),
    (False, False, False),  # installed wheel: never rebuild
])
def test_ensure_frontend(monkeypatch, checkout, up_to_date, rebuilt):
    """Only a stale frontend in a source checkout is rebuilt."""
    calls = []
    monkeypatch.setattr(launcher, 'is_source_checkout', lambda: checkout)
    monkeypatch.setattr(launcher, 'is_up_to_date', lambda: up_to_date)
    monkeypatch.setattr(launcher, 'build', lambda: calls.append(1))
    launcher.ensure_frontend()
    assert bool(calls) == rebuilt


def test_ensure_frontend_keeps_old_frontend_if_rebuild_fails(monkeypatch, capsys):
    """A failed rebuild (e.g. offline) is reported, the launcher goes on."""
    def failing_build():
        """Fail like `reflex export` without internet access.

        Raises:
            CalledProcessError: Always.
        """
        raise subprocess.CalledProcessError(1, 'reflex export')

    monkeypatch.setattr(launcher, 'is_source_checkout', lambda: True)
    monkeypatch.setattr(launcher, 'is_up_to_date', lambda: False)
    monkeypatch.setattr(launcher, 'build', failing_build)
    launcher.ensure_frontend()
    assert 'Rebuilding the frontend failed' in capsys.readouterr().err
