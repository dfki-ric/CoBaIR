# Changelog

All notable changes to this project are documented in this file.
Versions follow [semantic versioning](https://semver.org/); see [CONTRIBUTING.md](CONTRIBUTING.md).
References like `GitLab MR !123` point to the former internal GitLab project.

## Unreleased
- all dependencies are declared in `pyproject.toml`: the development tools are dependency groups (`pip install --group test|docs|lint|e2e`, pip >= 25.1), the `requirements/` folder is gone (#222) (patch)
- docs: migration guide 4.x → 5.0, docu is built with `--strict`, the old Qt GIFs of the Tutorial are replaced by web GUI screenshots (#209) (patch)
- the web GUI is deployed to a Hugging Face Docker Space on every release tag (`deploy/hf-space`, workflow `deploy_space`); CI builds and smoke-tests the Space image (#208) (patch)
- web GUI live inference: evidence per context (or unknown), bar chart of the intention probabilities with the decision threshold and the recognized intention, graph highlights the evidence and colors the intentions (#207) (minor)
- web GUI graph (React Flow): contexts, intentions and combined influences, edge thickness/color show the influence, clicking unfolds contexts and selects them in the editor (#182) (minor)
- the CI workflow is split into the workflows Tests (with the coverage badge), Build and Docs (#233) (patch)
- README badge for the test coverage of the `cobair` package: the CI workflow combines the coverage of the Python 3.12 tests (now with all extras on Python >= 3.11) and the end-to-end tests including the `cobair-web` server process (#231) (patch)
- web GUI editor: edit contexts, intentions, apriori probabilities, influences (human readable scale, #144), combined influences and the decision threshold; undo/redo; download YAML; `cobair-web config.yml` opens a file and saves to it; drafts are autosaved in the browser; warning before leaving with unsaved changes; info tooltips link to the Tutorial (minor)
- web GUI editor: editing an apriori probability or the decision threshold no longer takes the focus from the next input, also while the config is invalid in between (patch)
- web GUI editor: logo in the header and as favicon; sections and contexts can be folded; Ctrl+Z / Ctrl+Shift+Z / Ctrl+Y undo and redo; "unsaved changes" and the warning before leaving are only shown when `cobair-web` was started with a file, because without one the draft in the browser keeps all changes (patch)
- `cobair-web` rebuilds the frontend in a source checkout when the web GUI sources changed since the last build, instead of serving a stale frontend that keeps reloading (#228) (patch)
- Tutorial describes apriori probabilities, influence values, decision threshold and combined influences in more detail, with web GUI screenshots (#178 - #181) (patch)
- new web GUI `cobair-web` (Reflex, `[web]` extra): pre-built frontend shipped in the package and served with the backend on one port, no Node.js needed; needs Python >= 3.11, installing `[web]` or `[all]` on Python 3.10 fails instead of silently leaving out Reflex; load YAML files or the example and see contexts, intentions and validation problems (minor)
- CI builds the web GUI frontend into the wheel, checks the installed wheel serves it and runs Playwright end-to-end tests (patch)
- CI containers use Debian bookworm (bullseye is EOL) (patch)
- the Qt configurator moved to `cobair.qt` and works on `cobair.model.Config`; start it with the new command `cobair-qt [-f config.yml]`; `cobair.configurator` / `cobair.visualization` are deprecated aliases (minor)
- `[qt]` extra uses PyQt5 5.15.11 (5.15.9 segfaults with Python >= 3.12) and no longer needs `[infer]` (patch)
- Qt configurator: repeated actions no longer freeze or crash the GUI (callbacks were connected again on every update, the combined influence dialog deleted widgets twice), File > New no longer crashes, the window icon is found in pip installs, every combined influence has its own row in the advanced table, influence 1 is labelled "very low" (patch)
- dependencies bumped to their current versions: pgmpy 1.1.2, bnlearn 1.1.0 (numpy 2 and current setuptools allowed again), pyyaml >= 6.0.3, PyQt5 5.15.11, pyqtgraph 0.14.0, reflex 0.10.1; `BayesNet(bn_verbosity=...)` is ignored and `Inference` has no `verbosity` any more, bnlearn 1.x logs through `logging` (#224) (patch)
- new API: `cobair.model.Config` (pure Python: editing, validation, files, CPT computation) and `cobair.infer.Inference` (pgmpy/bnlearn adapter); `cobair.bayes_net` (`BayesNet`, `load_config`, ...) is deprecated and will be removed in 6.0.0 (minor)
- config files get a header comment and the keys `format_version` and `created_with`, keys keep their order instead of being sorted (minor)
- editing or deleting a context no longer deletes all combined influences, renaming a context renames it in the combined influences (patch)
- all combined influences of a context combination are used, not only the first one; `del_combined_influence` only removes the given combination (patch)
- discretization functions are applied to every value that is not an instantiation, not only to unhashable values (patch)
- renaming a context to an existing context raises a `ValueError` instead of overwriting it; apriori probabilities are checked to sum up to 1 with a tolerance (patch)
- the package is imported as `cobair` (lowercase) instead of `CoBaIR`; `import CoBaIR` still works until 6.0.0 but raises a `DeprecationWarning` (breaking)
- Python >= 3.10 is required, CI tests Python 3.10 - 3.13 (breaking)
- dependencies are split into install extras `[infer]`, `[qt]`, `[web]` and `[all]`; `pip install cobair` only installs the config model dependencies (breaking)
- packaging metadata moved to `pyproject.toml`, the package is built with `python -m build` (fixes the PyPI upload error with the normalized name, #196) (patch)
- the `.ui` files of the Qt configurator are part of the installed package (patch)
- docu is built with current mkdocstrings (patch)
- moved completely from GitLab to GitHub (issues, CI pipelines, templates)
- workflow with feature/fix branches into `main` only, releases are created from tags, docu is published on release tags
- `@claude` can be mentioned in issues and Pull Requests
- make scale more human readable
- refactoring of update config
- fixed graph bug
- require setuptools<81, pgmpy 0.1.20 still needs `pkg_resources` (fixes import errors on Python >= 3.10)
- code quality badges and Quality workflow: ruff linting issues and docstring coverage may not get worse than `.github/quality-baseline.json`; ruff replaces pylint; the Quality workflow also runs on Pull Requests, README badges are only committed on `main` (patch)

## 4.0.5 - 2026-04-21
- re-release of 4.0.4 to fix the PyPI upload (normalized package name `cobair`)

## 4.0.4 - 2026-04-21
- moved docu build pipeline to gitlab (patch) (GitLab MR !156)
- fix for save (patch) (GitLab MR !159)
- initialized current file name with None (patch) (GitLab MR !160)
- added citation section and adjusted deps for tests (patch) (GitLab MR !161)
- upgraded to actions/cache@v5 (patch) (GitLab MR !163)
- using twine upload --verbose now (patch) (GitLab MR !164)

## 4.0.3 - 2023-12-20
- moved building the docu to GitLab

## 4.0.2 - 2023-12-20
- added tutorial
- added tests for Python Versions 3.9, 3.10, 3.11
- adjusted link list for Papers in README to be displayed correctly in HTML

## 4.0.1 - 2023-08-29
- moved test related files to test folder (patch) (GitLab MR !147)
- added full paper in README

## 4.0.0 - 2023-08-10
- draw connections (patch)
- fixed layout warnings (patch) (GitLab MR !123)
- removed save_invalid from the method signature (breaking) (GitLab MR !124)
- added astrix on changes to the title
- moved TwoLayerGraph to visualization module (breaking) (GitLab MR !128)
- adjustment of labels (patch)
- create new config menu entry and shortcut
- fixed Bug with pop-up after clicking on graph (patch)
- Added GIF to Readme (patch) (GitLab MR !138)
- Match colors of graph and slider (minor) (GitLab MR !125)
- graph alignment (patch) (GitLab MR !126)
- Issue and MR templates (minor) (GitLab MR !142)
- Added GUI Test Protocol (minor) (GitLab MR !113)
- clearing sliders correctly for invalid config (patch) (GitLab MR !132)
- fixed bug in button for deleting context (patch) (GitLab MR !131)
- Activate corresponding fields in GUI by clicking on graph (minor) (GitLab MR !133)
- Logging (minor) (GitLab MR !134)
- Warnings for evidence that will be ignored (breaking) (GitLab MR !139)
- Changed assert to warn (breaking) (GitLab MR !136)
- Enhanced connection style (minor) (GitLab MR !135)
- Fix for problem with official pyqtgraph version (patch) (GitLab MR !144)
- New Logo (minor) (GitLab MR !145)
- Fixed layout bugs (minor) (GitLab MR !146)

## 3.0.0 - 2023-05-09
- QT Version bump(minor)
- Layout moved completely to UI file
- Slider colors (patch)
- error handling for "new combined context" (patch)
- changed the way layout elements are accessed (patch)
- change of return to transport decision_threshold (breaking)

## 2.1.0 - 2023-04-17
- Graph Viz (Minor)
- some docu (patch)

## 2.0.5 - 2023-03-17
- fixed dependency versions (bnlearn==0.7.10 with pgmpy==0.1.20)
- docu published on GitHub Pages
- more info for the PyPI package
- adjusted manifest

## 2.0.0 - 2023-03-15
- create, edit and delete contexts and intentions in the GUI
- new combined context influence
- how to contribute section in README

## 1.1.0 - 2022-09-12
- supports removing instantiations and validation on that(minor)

## 1.0.1 - 2022-09-09
- fixed bug with max_intention - now correctly using the normalized inference

## 1.0.0 - 2022-09-09
- visual bug with showing combined context(patch)
- using pytest instead of unittest now (patch)
- using coverage and providing badges (patch)
- providing test and coverage reports in GitLab (patch)
- introduced decision threshold and provide results from infer as tuple of intention with the highest likelihood and distribution of all intentions(major)
- support for decision_threshold in config file and GUI

## 0.2.2 - 2022-05-25
- hotfix for Discretizer Functions returning None

## 0.2.1 - 2022-05-18
- adjusted readme
- fix for import
- Extended config
- GUI for extended config

## 0.1.1 - 2022-02-14
- This version reduces bnlearn output

## 0.1.0 - 2022-02-14
- Now supporting edit and delete in configurator and None values in evidence

## 0.0.0 - 2022-02-08
- First Version
