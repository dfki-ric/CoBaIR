"""Build the static frontend of the web GUI into `cobair/web/frontend` (package data).

Run `python -m cobair.web.build` before building the wheel. Reflex downloads the JavaScript tools it
needs; users of the wheel don't need them.
"""

# System imports
import os
import shutil
import subprocess
import sys

# 3rd party imports

# local imports
from . import FRONTEND_DIR, PROJECT_DIR

# end file header
__author__ = 'Adrian Lubitz'


def build() -> None:
    """Export the frontend with Reflex and copy it to `FRONTEND_DIR`."""
    env = dict(os.environ, REFLEX_TELEMETRY_ENABLED='false')
    subprocess.run([sys.executable, '-m', 'reflex', 'export', '--frontend-only', '--no-zip'],
                   cwd=PROJECT_DIR, env=env, check=True)
    shutil.rmtree(FRONTEND_DIR, ignore_errors=True)
    shutil.copytree(PROJECT_DIR / '.web' / 'build' / 'client', FRONTEND_DIR)
    print(f'Frontend built to {FRONTEND_DIR}')


if __name__ == '__main__':
    build()
