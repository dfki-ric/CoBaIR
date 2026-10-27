# Web GUI

The web GUI is the primary GUI of CoBaIR. Install and start it with

```bash
pip install "cobair[web]"
cobair-web
```

`cobair-web` serves the GUI on <http://localhost:8000> and opens it in your browser.
No Node.js is needed: the frontend is pre-built and part of the package.

| option | |
|---|---|
| `--port 8000` | port to listen on |
| `--host 127.0.0.1` | host to listen on, use `0.0.0.0` to open the GUI to other machines |
| `--no-browser` | don't open the browser |

![The CoBaIR web GUI](images/web_gui.png)

## Configs
Load a config with **Load YAML** (or drop a file on the button) or start with **Load example**.
The configs stay on your machine, the GUI only keeps them in memory while the page is open.

## For developers
The web GUI is a [Reflex](https://reflex.dev) app in `cobair/web` (Reflex is pinned to an exact version).

- Run it with hot reload: `cd cobair/web && reflex run`
- Build the frontend that is shipped in the package: `python -m cobair.web.build`
  (Reflex downloads the JavaScript tools it needs)
- Tests: `pytest tests/web`. The end-to-end tests start `cobair-web` and need the built frontend and
  Playwright (`pip install playwright && playwright install chromium`).
