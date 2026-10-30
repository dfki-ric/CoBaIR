"""Tests for deploy/hf-space/deploy.py (the upload itself needs Hugging Face)."""

# System imports
import importlib.util
from pathlib import Path

# 3rd party imports
import pytest

# local imports

# end file header
__author__ = 'Adrian Lubitz'

SPACE_DIR = Path(__file__).resolve().parents[1] / 'deploy' / 'hf-space'
spec = importlib.util.spec_from_file_location('deploy_space', SPACE_DIR / 'deploy.py')
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


def test_stage(tmp_path):
    """The Space gets the Dockerfile, the Space card and the wheel."""
    dist = tmp_path / 'dist'
    dist.mkdir()
    (dist / 'cobair-5.0.0-py3-none-any.whl').write_bytes(b'wheel')
    (dist / 'cobair-5.0.0.tar.gz').write_bytes(b'sdist')
    target = tmp_path / 'space'
    target.mkdir()
    deploy.stage(target, dist)
    assert sorted(path.relative_to(target).as_posix() for path in target.rglob('*')) == [
        'Dockerfile', 'README.md', 'dist', 'dist/cobair-5.0.0-py3-none-any.whl']


@pytest.mark.parametrize('wheels', [0, 2])
def test_stage_needs_one_wheel(tmp_path, wheels):
    """Exactly one wheel must be built."""
    for index in range(wheels):
        (tmp_path / f'cobair-5.0.{index}-py3-none-any.whl').write_bytes(b'wheel')
    with pytest.raises(SystemExit):
        deploy.stage(tmp_path, tmp_path)


def test_space_card():
    """The Space card configures a Docker Space on the port the Dockerfile serves."""
    card = (SPACE_DIR / 'README.md').read_text(encoding='utf-8')
    dockerfile = (SPACE_DIR / 'Dockerfile').read_text(encoding='utf-8')
    assert 'sdk: docker' in card and 'app_port: 7860' in card
    assert '"--port", "7860"' in dockerfile and 'USER user' in dockerfile
