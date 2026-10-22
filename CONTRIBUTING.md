# Contributing to CoBaIR

Thanks for your interest in CoBaIR! Bugs, feature requests and questions are welcome as
[issues](https://github.com/dfki-ric/CoBaIR/issues) - please use the matching issue template.

## Development workflow

- `main` holds the latest release, `develop` the current state of development.
- Every change starts with an issue. Create a branch from `develop` named after the issue,
  e.g. `171-graph-bug`, and open a Pull Request into `develop`.
- The [CI pipeline](https://github.com/dfki-ric/CoBaIR/actions/workflows/ci.yml) runs tests for all supported
  Python versions, pylint, the docu build and the package build. All checks must pass before merging.
- Add tests for new functionality (see the README on how to run tests and coverage) and add a line
  to the `Unreleased` section of [CHANGELOG.md](CHANGELOG.md).

## Versioning

CoBaIR uses [semantic versioning](https://semver.org/) `MAJOR.MINOR.PATCH`.
Each change is classified when it is merged into `develop`:

- **breaking** - incompatible API or config format changes -> bump `MAJOR`
- **minor** - new, backwards compatible functionality -> bump `MINOR`
- **patch** - backwards compatible bug fixes, docu, CI -> bump `PATCH`

The new version is determined by the most significant change since the last release.

## Releasing

1. Open a Pull Request from `develop` into `main` using the version template. Its title is the new version,
   its description lists all changes since the last release with their classification and links to the PRs.
2. Before merging: check that all tests pass and perform the manual GUI tests documented in
   [tests/gui_test_protocol.md](tests/gui_test_protocol.md).
3. Merge, move the `Unreleased` entries in [CHANGELOG.md](CHANGELOG.md) to a section for the new version and
   create a tag named exactly like the version (e.g. `4.1.0`, no `v` prefix) on `main`.
4. Pushing the tag triggers the [release workflow](.github/workflows/release.yml), which builds the package
   with the tag as version and uploads it to [PyPI](https://pypi.org/project/cobair/).
   The docu on [GitHub Pages](https://dfki-ric.github.io/CoBaIR/) is updated on every push to `main`.
5. Create a GitHub Release from the tag with the changelog of the version.
