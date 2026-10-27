"""`cobair-web`: serve the pre-built frontend and the Reflex backend on one port.

No Node.js is needed: the frontend is built in CI (`python -m cobair.web.build`) and shipped in the
wheel, the backend mounts it like `reflex run --env prod --single-port` does.
"""

# System imports
import argparse
import atexit
import os
import shutil
import sys
import tempfile
import threading
import webbrowser
from pathlib import Path

# 3rd party imports

# local imports
from . import FRONTEND_DIR, PROJECT_DIR

#: Same as `cobair.web.state.FILE_ENV`, not imported to keep the start fast.
FILE_ENV = 'COBAIR_WEB_FILE'

# end file header
__author__ = 'Adrian Lubitz'

DEFAULT_PORT = 8000


def prepare_runtime_dir(runtime_dir: Path, port: int) -> None:
    """Put the Reflex config and a copy of the frontend for `port` into `runtime_dir`.

    The frontend has the backend URL `http://localhost:8000` built in. The browser replaces
    `localhost` by the host of the page, only the port needs to be changed here.

    Args:
        runtime_dir: An empty directory which becomes the working directory of the backend.
        port: The port the backend listens on.

    Raises:
        FileNotFoundError: If the frontend was not built.
    """
    if not (FRONTEND_DIR / 'index.html').exists():
        raise FileNotFoundError(
            f'The web GUI frontend is missing in {FRONTEND_DIR}. '
            'Build it with `python -m cobair.web.build` (needs internet access) '
            'or install cobair from PyPI.')
    shutil.copy(PROJECT_DIR / 'rxconfig.py', runtime_dir / 'rxconfig.py')
    client = runtime_dir / '.web' / 'build' / 'client'
    shutil.copytree(FRONTEND_DIR, client)
    if port != DEFAULT_PORT:
        for env_file in client.glob('assets/reflex-env-*.js'):
            env_file.write_text(env_file.read_text(encoding='utf-8').replace(
                f'localhost:{DEFAULT_PORT}', f'localhost:{port}'), encoding='utf-8')
            # precompressed variants would still contain the old port
            for compressed in client.glob(f'assets/{env_file.name}.*'):
                compressed.unlink()


def serve(host: str, port: int) -> None:
    """Run the Reflex backend with the mounted frontend in the current working directory.

    Args:
        host: The host to listen on.
        port: The port to listen on.
    """
    # pylint: disable=import-outside-toplevel
    from reflex_base import constants
    from reflex_base.environment import environment

    environment.REFLEX_ENV_MODE.set(constants.Env.PROD)
    environment.REFLEX_SKIP_COMPILE.set(True)

    from reflex.utils import exec as reflex_exec

    reflex_exec.run_backend_prod(host, port, constants.LogLevel.INFO,
                                 mount_frontend_compiled_app=True)


def main(argv: list = None) -> int:
    """Start the web GUI, the entry point of `cobair-web`.

    Args:
        argv: Command line arguments, defaults to `sys.argv[1:]`.

    Returns:
        int: The exit code.
    """
    parser = argparse.ArgumentParser(prog='cobair-web', description='CoBaIR web GUI')
    parser.add_argument('file', nargs='?',
                        help='Config file to open; the GUI can save to it. Without a file, '
                             'configs are only up- and downloaded.')
    parser.add_argument('--host', default='127.0.0.1',
                        help='Host to listen on, use 0.0.0.0 to allow other machines '
                             '(default: %(default)s)')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT,
                        help='Port to listen on (default: %(default)s)')
    parser.add_argument('--no-browser', action='store_true',
                        help="Don't open the web GUI in the browser")
    args = parser.parse_args(argv)

    runtime_dir = Path(tempfile.mkdtemp(prefix='cobair-web-'))
    atexit.register(shutil.rmtree, runtime_dir, ignore_errors=True)
    try:
        prepare_runtime_dir(runtime_dir, args.port)
    except FileNotFoundError as error:
        print(error, file=sys.stderr)
        return 1

    if args.file:
        # read by the state of every worker
        os.environ[FILE_ENV] = str(Path(args.file).resolve())
    url = f'http://localhost:{args.port}'
    print(f'CoBaIR web GUI: {url}')
    if not args.no_browser:
        threading.Timer(2.0, webbrowser.open, args=(url,)).start()

    os.chdir(runtime_dir)
    serve(args.host, args.port)
    return 0


if __name__ == '__main__':
    sys.exit(main())
