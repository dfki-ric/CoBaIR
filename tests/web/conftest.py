"""Fixtures for the end-to-end tests: a running `cobair-web` and a browser page."""

# System imports
import os
import socket
import subprocess
import sys
import time
import urllib.request

# 3rd party imports
import pytest

# end file header
__author__ = 'Adrian Lubitz'


def free_port() -> int:
    """Return a free TCP port.

    Returns:
        int: The port.
    """
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


@pytest.fixture(scope='session')
def web_url(tmp_path_factory):
    """Start `cobair-web` with the pre-built frontend, like a user would.

    Yields:
        str: The URL of the web GUI.
    """
    pytest.importorskip('reflex')
    from cobair.web import FRONTEND_DIR  # pylint: disable=import-outside-toplevel
    if not (FRONTEND_DIR / 'index.html').exists():
        pytest.skip('frontend not built, run `python -m cobair.web.build`')
    port = free_port()
    log = tmp_path_factory.mktemp('web') / 'cobair-web.log'
    with open(log, 'w', encoding='utf-8') as log_file:
        process = subprocess.Popen(  # pylint: disable=consider-using-with
            [sys.executable, '-m', 'cobair.web.launcher', '--port', str(port), '--no-browser'],
            stdout=log_file, stderr=subprocess.STDOUT, env=dict(os.environ))
    url = f'http://localhost:{port}'
    try:
        for _ in range(120):
            try:
                urllib.request.urlopen(f'{url}/ping', timeout=1)  # noqa: S310
                break
            except OSError:
                if process.poll() is not None:
                    pytest.fail(f'cobair-web exited:\n{log.read_text()}')
                time.sleep(0.5)
        else:
            pytest.fail(f'cobair-web did not start:\n{log.read_text()}')
        yield url
    finally:
        process.terminate()
        process.wait(timeout=30)


@pytest.fixture(scope='session')
def browser():
    """A headless Chromium.

    Yields:
        playwright.sync_api.Browser: The browser.
    """
    sync_api = pytest.importorskip('playwright.sync_api')
    with sync_api.sync_playwright() as playwright:
        chromium = playwright.chromium.launch()
        yield chromium
        chromium.close()


@pytest.fixture
def page(browser, web_url):
    """A new page with the web GUI loaded.

    Yields:
        playwright.sync_api.Page: The page.
    """
    context = browser.new_context(viewport={'width': 1280, 'height': 900})
    new_page = context.new_page()
    new_page.set_default_timeout(15000)
    new_page.goto(web_url)
    new_page.wait_for_selector('#load-example')
    yield new_page
    context.close()
