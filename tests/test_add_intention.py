'''
Tests for adding intention variables
'''

# System imports
import pytest
from collections import defaultdict
import warnings
# 3rd party imports

# local imports
from tests import N
from CoBaIR.bayes_net import BayesNet, config_to_default_dict, default_to_regular, load_config

# end file header
__author__ = 'Adrian Lubitz'

# TODO: add more negative cases

def test_add_to_empty(config=None, counter=0):
    """
    Test adding an intention to an empty config
    """
    if config is None:
        config = {'intentions': defaultdict(lambda: defaultdict(
            lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}
        bn = BayesNet()
    else:
        bn = BayesNet(config, validate=False)
    intention = f'some intention_{counter}'

    config['intentions'][intention] = {}

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")  # Ensure all warnings are caught
        bn.add_intention(intention)
        assert len(w) == 1  # Check that one warning was raised
        assert issubclass(w[-1].category, UserWarning)  # Check that the warning is a UserWarning

    # Making sure tmp_config will be maintained
    assert config_to_default_dict(bn.config) == config_to_default_dict(config)

def test_add_n_to_empty(n=N):
    """
    Test adding n intentions to an empty config
    """
    config = {'intentions': defaultdict(lambda: defaultdict(
        lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}
    for i in range(n):
        test_add_to_empty(config, i)

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
