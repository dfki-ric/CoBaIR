'''
Tests for Loading yaml format config file
'''

# System imports
import pytest
from collections import defaultdict
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

    config = load_config('small_example_invalid.yml')

    # I assume this will throw an Error!- AssertionError: Influence Value for pick up tool.speech commands.handover must be an integer between 0 and 5! Is 10
    with pytest.raises(AssertionError):
        BayesNet(config)
        assert BayesNet(config).valid == False


def test_loading_valid_yml_file():
    """
    Test loading valid file name - validata_config() function will validate that the current config follows the correct format.
    """

    config = load_config('small_example.yml')
    bn = BayesNet(config)
    # valid config
    assert bn.valid == True
