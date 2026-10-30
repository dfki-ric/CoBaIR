"""Build the static frontend of the web GUI into `cobair/web/frontend` (package data).

Run `python -m cobair.web.build` before building the wheel. Reflex downloads the JavaScript tools it
needs; users of the wheel don't need them.

The build writes a hash of the web GUI sources to `STAMP_FILE`. In a source checkout `cobair-web`
compares it with the current sources and rebuilds a stale frontend.
"""

# System imports
import hashlib
import os
import shutil
import subprocess
import sys
from importlib import metadata
from pathlib import Path

# 3rd party imports

# local imports
from . import FRONTEND_DIR, PROJECT_DIR

# end file header
__author__ = 'Adrian Lubitz'

#: The hash of the sources the frontend was built from.
STAMP_FILE = FRONTEND_DIR / 'build-hash.txt'
#: Modules that don't end up in the frontend.
NOT_IN_FRONTEND = {'build.py', 'launcher.py'}


def source_hash(project_dir: Path = PROJECT_DIR) -> str:
    """Hash everything the frontend is compiled from: the Python sources and the Reflex version.

    Args:
        project_dir: The Reflex project directory.

    Returns:
        str: The hex digest.
    """
    digest = hashlib.sha256(metadata.version('reflex').encode())
    for path in sorted(project_dir.rglob('*.py')):
        relative = path.relative_to(project_dir)
        # build output (.web, frontend) and caches
        generated = any(part.startswith('.') or part in ('frontend', '__pycache__')
                        for part in relative.parts)
        if generated or path.name in NOT_IN_FRONTEND:
            continue
        digest.update(relative.as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def is_up_to_date() -> bool:
    """Check whether the frontend was built from the current sources.

    Returns:
        bool: False if the frontend is missing or the sources changed since it was built.
    """
    if not (FRONTEND_DIR / 'index.html').exists() or not STAMP_FILE.exists():
        return False
    return STAMP_FILE.read_text(encoding='utf-8').strip() == source_hash()


def build() -> None:
    """Export the frontend with Reflex and copy it to `FRONTEND_DIR`."""
    env = dict(os.environ, REFLEX_TELEMETRY_ENABLED='false')
    subprocess.run([sys.executable, '-m', 'reflex', 'export', '--frontend-only', '--no-zip'],
                   cwd=PROJECT_DIR, env=env, check=True)
    shutil.rmtree(FRONTEND_DIR, ignore_errors=True)
    shutil.copytree(PROJECT_DIR / '.web' / 'build' / 'client', FRONTEND_DIR)
    STAMP_FILE.write_text(source_hash() + '\n', encoding='utf-8')
    print(f'Frontend built to {FRONTEND_DIR}')


if __name__ == '__main__':
    build()
