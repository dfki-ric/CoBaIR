"""Deprecated alias for the `cobair` package, kept so that `import CoBaIR.bayes_net` still works.

This is a module and not a package directory, because `CoBaIR/` and `cobair/`
can't coexist on case-insensitive file systems (macOS, Windows).
Submodules are imported lazily: `CoBaIR.<name>` is the very same module object as `cobair.<name>`.
"""

# System imports
import importlib
import importlib.abc
import importlib.util
import sys
import warnings

# 3rd party imports

# local imports
import cobair

# end file header
__author__ = 'Adrian Lubitz'

warnings.warn("The package 'CoBaIR' was renamed to 'cobair'. "
              "'import CoBaIR' will be removed in 6.0.0.", DeprecationWarning, stacklevel=2)

# makes this module a package, so that the import system looks for submodules
__path__ = []
__version__ = cobair.__version__


class _AliasFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Resolve `CoBaIR.<name>` to the already existing module `cobair.<name>`."""

    prefix = __name__ + '.'
    is_cobair_alias_finder = True

    def __init__(self):
        self.original_specs = {}

    def find_spec(self, fullname, path, target=None):
        """Return a spec for every submodule of `CoBaIR`.

        Args:
            fullname: The fully qualified name of the module to import.
            path: The `__path__` of the parent package.
            target: Unused, see `importlib.abc.MetaPathFinder`.

        Returns:
            A module spec or None if the module is not a submodule of `CoBaIR`.
        """
        if not fullname.startswith(self.prefix):
            return None
        target_name = 'cobair.' + fullname[len(self.prefix):]
        if importlib.util.find_spec(target_name) is None:
            return None
        return importlib.util.spec_from_loader(fullname, self)

    def create_module(self, spec):
        """Return the `cobair` module instead of creating a new one.

        Args:
            spec: The spec of the `CoBaIR` submodule.

        Returns:
            The corresponding `cobair` module.
        """
        module = importlib.import_module('cobair.' + spec.name[len(self.prefix):])
        self.original_specs[module.__name__] = module.__spec__
        return module

    def exec_module(self, module):
        """Restore the spec of the `cobair` module, the module itself is already executed.

        The import system sets `__spec__` of the module returned by `create_module` to the
        `CoBaIR` spec, which would break e.g. `importlib.reload` of the `cobair` module.

        Args:
            module: The module returned by `create_module`.
        """
        module.__spec__ = self.original_specs.pop(module.__name__)


# compare by attribute, the class is a new one if this module is executed again
if not any(getattr(finder, 'is_cobair_alias_finder', False) for finder in sys.meta_path):
    sys.meta_path.insert(0, _AliasFinder())
