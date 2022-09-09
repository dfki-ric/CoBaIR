'''
Tests for adding intention variables
'''

# System imports
import pytest
from collections import defaultdict
# 3rd party imports

# local imports
from tests import N
from CoBaIR.bayes_net import BayesNet, config_to_default_dict, default_to_regular, load_config

# end file header
__author__ = 'Adrian Lubitz'

# TODO: add more negative cases


def test_add_to_empty():
    """
    Test adding an intention to an empty config
    """
    config = {'intentions': defaultdict(lambda: defaultdict(
        lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}
    intention = 'some intention'

    config['intentions'][intention] = {}
    bn = BayesNet()
    # I assume this will throw an Error!
    with pytest.raises(AssertionError):
        bn.add_intention('some intention')
    # Making sure tmp_config will be maintained
    assert config_to_default_dict(bn.config) == config_to_default_dict(config)


def test_add_n_to_empty(n=N):
    """
    Test adding n intentions to an empty config
    """
    config = {'intentions': defaultdict(lambda: defaultdict(
        lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}
    intention = 'intention'
    bn = BayesNet()
    # I assume this will throw an Error!
    for i in range(n):
        config['intentions'][f'{intention}_{i}'] = {}
        with pytest.raises(AssertionError):
            bn.add_intention(f'{intention}_{i}')
    # Making sure tmp_config will be maintained
    assert config_to_default_dict(bn.config) == config_to_default_dict(config)


def test_add_to_existing():
    """
    Test adding an intention to an existing config
    """
    config = load_config('small_example.yml')
    bn = BayesNet(config)
    bn.add_intention('some intention')


def test_add_n_to_existing(n=N):
    """
    Test adding n intentions to an existing config
    """
    config = load_config('small_example.yml')
    bn = BayesNet(config)
    for i in range(n):
        bn.add_intention(f'intention_{i}')


def test_add_to_existing_loaded():
    """
    Test adding an intention to an existing config
    """
    bn = BayesNet()
    bn.load('small_example.yml')
    bn.add_intention('some intention')


def test_add_n_to_existing_loaded(n=N):
    """
    Test adding n intentions to an existing config
    """
    bn = BayesNet()
    bn.load('small_example.yml')
    for i in range(n):
        bn.add_intention(f'intention_{i}')
