"""Deprecated alias of `cobair.qt.visualization`, removed in 6.0.0."""

import warnings

from .qt.visualization import *  # noqa: F401,F403

warnings.warn("'cobair.visualization' moved to 'cobair.qt.visualization'. "
              "The alias will be removed in 6.0.0.", DeprecationWarning, stacklevel=2)
