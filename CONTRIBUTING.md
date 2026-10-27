# Contributing to CoBaIR

Thanks for your interest in CoBaIR! Bugs, feature requests and questions are welcome as
[issues](https://github.com/dfki-ric/CoBaIR/issues) - please use the matching issue template.

## Development workflow

- `main` is the only long-lived branch. It always has to be in a working state.
- Every change starts with an issue. Create a short-lived branch from `main` named after the type of change
  and the issue, e.g. `feature/153-live-inference` or `fix/171-graph-bug`, and open a Pull Request into `main`.
- The [CI pipeline](https://github.com/dfki-ric/CoBaIR/actions/workflows/ci.yml) runs tests for all supported
  Python versions, the docu build and the package build on every Pull Request.
  The [Quality workflow](https://github.com/dfki-ric/CoBaIR/actions/workflows/quality.yml) counts ruff linting issues
  and the docstring coverage and fails if one of them got worse than `.github/quality-baseline.json`
  (see [Code quality](README.md#code-quality)). All checks must pass before merging.
- The web GUI (`cobair/web`) is a [Reflex](https://reflex.dev) app, see the
  [developer notes](docs/WebGUI.md#for-developers). Reflex is pinned exactly and only upgraded
  deliberately, together with the end-to-end tests (`tests/web`).
- Add tests for new functionality (see the README on how to run tests and coverage) and add a line
  to the `Unreleased` section of [CHANGELOG.md](CHANGELOG.md), marked as breaking, minor or patch.

### Working with Claude

Mention `@claude` in an issue, a Pull Request or a comment to let Claude work on it. Claude answers in the
issue or Pull Request. For code changes it pushes a `claude/...` branch and posts a link to open a Pull Request
into `main`, which is reviewed like any other.
Only users with write access to the repository can trigger Claude.

## Versioning

CoBaIR uses [semantic versioning](https://semver.org/) `MAJOR.MINOR.PATCH`.
Each change is classified in the changelog:

- **breaking** - incompatible API or config format changes -> bump `MAJOR`
- **minor** - new, backwards compatible functionality -> bump `MINOR`
- **patch** - backwards compatible bug fixes, docu, CI -> bump `PATCH`

The new version is determined by the most significant change since the last release.

## Releasing

A version is created by tagging a commit on `main`.

1. Open a Pull Request that moves the `Unreleased` entries in [CHANGELOG.md](CHANGELOG.md) to a section for the
   new version, e.g. `## 4.1.0 - 2026-11-02`.
2. Before merging: check that all tests pass and perform the manual GUI tests documented in
   [tests/gui_test_protocol.md](tests/gui_test_protocol.md).
3. After merging, create a GitHub Release on `main` with a new tag named exactly like the version
   (e.g. `4.1.0`, no `v` prefix) and the changelog of the version as description.
4. The tag triggers
   - the [release workflow](.github/workflows/release.yml), which builds the package with the tag as version
     and uploads it to [PyPI](https://pypi.org/project/cobair/),
   - the [docu workflow](.github/workflows/publishDocu.yml), which publishes the docu of this version on
     [GitHub Pages](https://dfki-ric.github.io/CoBaIR/).
