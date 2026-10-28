"""Tests for the deprecated `CoBaIR` import name."""

# System imports
import importlib
import sys
import warnings

# 3rd party imports
import pytest

# local imports
import cobair.bayes_net

# end file header
__author__ = 'Adrian Lubitz'


@pytest.fixture
def fresh_CoBaIR():
    """Remove `CoBaIR` from the module cache, so that importing it runs the module again."""
    for name in [name for name in sys.modules if name == 'CoBaIR' or name.startswith('CoBaIR.')]:
        del sys.modules[name]
    yield
    for name in [name for name in sys.modules if name == 'CoBaIR' or name.startswith('CoBaIR.')]:
        del sys.modules[name]


def test_import_warns(fresh_CoBaIR):
    """Importing `CoBaIR` raises a DeprecationWarning."""
    with pytest.warns(DeprecationWarning, match="renamed to 'cobair'"):
        importlib.import_module('CoBaIR')


def test_submodule_is_same_module(fresh_CoBaIR):
    """`CoBaIR.bayes_net` is the very same module as `cobair.bayes_net`."""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        from CoBaIR.bayes_net import BayesNet  # pylint: disable=import-outside-toplevel
        import CoBaIR.bayes_net  # pylint: disable=import-outside-toplevel
    assert BayesNet is cobair.bayes_net.BayesNet
    assert CoBaIR.bayes_net is cobair.bayes_net
    assert cobair.bayes_net.__name__ == 'cobair.bayes_net'
    assert cobair.bayes_net.__spec__.name == 'cobair.bayes_net'


def test_unknown_submodule(fresh_CoBaIR):
    """Submodules that don't exist in `cobair` don't exist in `CoBaIR` either."""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module('CoBaIR.does_not_exist')


def test_finder_installed_once(fresh_CoBaIR):
    """Importing `CoBaIR` again does not add another finder."""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        importlib.import_module('CoBaIR')
        for name in [name for name in sys.modules if name == 'CoBaIR']:
            del sys.modules[name]
        importlib.import_module('CoBaIR')
    assert sum(getattr(finder, 'is_cobair_alias_finder', False) for finder in sys.meta_path) == 1
