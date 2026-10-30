"""The web GUI of CoBaIR, built with [Reflex](https://reflex.dev).

Needs the `[web]` extra: `pip install "cobair[web]"`. Start it with `cobair-web`.
"""

from pathlib import Path

#: The Reflex project directory (contains rxconfig.py).
PROJECT_DIR = Path(__file__).parent
#: The pre-built frontend, created by `python -m cobair.web.build`.
FRONTEND_DIR = PROJECT_DIR / 'frontend'
