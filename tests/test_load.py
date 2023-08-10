'''
Tests for Loading yaml format config file
'''

# System imports
from collections import defaultdict
import pytest
import warnings
# 3rd party imports
from yaml.parser import ParserError

# local imports
from tests import N
from CoBaIR.bayes_net import BayesNet, load_config

# end file header
__author__ = 'Arunima Gopikrishnan'

# TODO: add more negative cases


def test_loading_invalid_file_format():
    """
    Test loading invalid file format.
    """

    # I assume this will throw an Error!
    with pytest.raises(ParserError):
        load_config('README.md')


def test_loading_non_existing_file():
    """
    Test loading non existing file.
    """

    # I assume this will throw an Error!
    with pytest.raises(FileNotFoundError):
        load_config('EATME.md')


def test_loading_invalid_file_name():
    """
    Test loading invalid file name - try to loading non-existing file name
    """

    # I assume this will throw an Error!
    with pytest.raises(FileNotFoundError):
        load_config('small.yml')


def test_loading_invalid_yml_file():
    """
    Test loading invalid file name
    """
    config = load_config('tests/small_example_invalid.yml')

    # I assume this will throw a warning instead of an error
    # if the value for pick up tool.speech commands.handover is invalid
    with pytest.warns(UserWarning):
        # Pass validate=True to enable config validation
        bn = BayesNet(config, validate=True)
        assert bn.valid is False


def test_no_intention_defined():
    """
    Test loading a configuration file with no intention defined
    """
    config = load_config('tests/small_example_invalid_intention.yml')

    # I assume this will throw a warning instead of an error
    with pytest.warns(UserWarning):
        # Pass validate=True to enable config validation
        bn = BayesNet(config, validate=True)
        assert bn.valid is False


def test_invalid_values():
    """
    Test loading a configuration file with values not in the correct range
    """
    config = load_config('tests/small_example_invalid_value.yml')

    # I assume this will throw a warning instead of an error
    with pytest.warns(UserWarning):
        # Pass validate=True to enable config validation
        bn = BayesNet(config, validate=True)
        assert bn.valid is False


def test_loading_valid_yml_file():
    """
    Test loading valid file name - validata_config() function will validate
        that the current config follows the correct format.
    """

    config = load_config('small_example.yml')
    # Pass validate=True to enable config validation
    bayes_net = BayesNet(config, validate=True)
    # valid config
    assert bayes_net.valid is True