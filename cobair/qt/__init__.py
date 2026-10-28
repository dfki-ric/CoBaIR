"""The Qt configurator of CoBaIR (maintenance mode, the web GUI is the primary GUI).

Needs the `[qt]` extra: `pip install "cobair[qt]"`. Start it with `cobair-qt [-f config.yml]`.
"""

from .configurator import Configurator, main

__all__ = ['Configurator', 'main']
