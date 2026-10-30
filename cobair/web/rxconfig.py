"""Reflex config of the CoBaIR web GUI, the project root is this directory."""

import sys
from pathlib import Path

import reflex as rx

import cobair

# Reflex looks for the app module by walking the sys.path directories, which misses editable
# installs (they use an import hook). The directory containing the cobair package fixes that.
_PACKAGE_ROOT = str(Path(cobair.__file__).resolve().parents[1])
if _PACKAGE_ROOT not in sys.path:
    sys.path.append(_PACKAGE_ROOT)

#: The port the frontend is built for, `cobair-web --port` rewrites it at launch.
DEFAULT_PORT = 8000

config = rx.Config(
    app_name='cobair_web',
    app_module_import='cobair.web.app',
    api_url=f'http://localhost:{DEFAULT_PORT}',
    backend_port=DEFAULT_PORT,
    frontend_port=3000,
    telemetry_enabled=False,
    show_built_with_reflex=False,
    plugins=[rx.plugins.RadixThemesPlugin()],
    disable_plugins=['reflex_base.plugins.sitemap.SitemapPlugin'],
)
