"""Deprecated alias of `cobair.qt.configurator`, removed in 6.0.0."""

import warnings

from .qt.configurator import *  # noqa: F401,F403

warnings.warn("'cobair.configurator' moved to 'cobair.qt.configurator'. "
              "The alias will be removed in 6.0.0.", DeprecationWarning, stacklevel=2)
