---
title: CoBaIR Editor
emoji: 🤖
colorFrom: yellow
colorTo: red
sdk: docker
app_port: 7860
pinned: false
license: bsd-3-clause
short_description: Configure and test context based intention recognition
---

# CoBaIR Editor

Web GUI of [CoBaIR](https://github.com/dfki-ric/CoBaIR), a Python library for **Co**ntext **Ba**sed
**I**ntention **R**ecognition. Create a configuration, see it as a graph and test the inference live.

Configs are not stored on this Space: load and download them as YAML files, unsaved drafts are kept in your browser.
To run the editor locally:

```bash
pip install "cobair[web]"
cobair-web
```

This Space is deployed automatically from the release tags of the GitHub repository, see the
[documentation](https://dfki-ric.github.io/CoBaIR/).
