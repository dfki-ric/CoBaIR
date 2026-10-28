"""CoBaIR - Context Based Intention Recognition."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version('cobair')
except PackageNotFoundError:  # pragma: no cover - running from a source checkout
    __version__ = 'dev'
