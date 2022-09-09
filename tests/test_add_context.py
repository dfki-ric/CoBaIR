'''
Tests for adding context variables
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


def test_add_to_empty(config=None, counter=0):
    """
    Test adding a context to an empty config
    """
    # bn = None  # is needed because bn will only exist in with statement otherwise
    if config == None:
        config = {'intentions': defaultdict(lambda: defaultdict(
            lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}
        bn = BayesNet()
    else:
        # with pytest.raises(AssertionError):
        bn = BayesNet(config, validate=False)
    context = f'the context_{counter}'
    instantiations = {
        f'inst_a_{counter}': 0.3, f'inst_b_{counter}': 0.3, f'inst_c_{counter}': 0.4}

    config['contexts'][context] = instantiations

    # I assume this will throw an Error!
    with pytest.raises(AssertionError):
        bn.add_context(context, instantiations)
    # Making sure tmp_config will be maintained
    assert config_to_default_dict(bn.config) == config_to_default_dict(config)


def test_add_n_to_empty(n=N):
    """
    Test adding n contexts to an empty config
    """
    config = {'intentions': defaultdict(lambda: defaultdict(
        lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}
    for i in range(n):
        test_add_to_empty(config, i)


@pytest.mark.timeout(1)
def test_add_to_existing(config=None, counter=0):
    """
    Test adding a context to an existing config
    """
    if config == None:
        config = load_config('small_example.yml')
    bn = BayesNet(config)
    context = f'the context_{counter}'
    instantiations = {
        f'inst_a_{counter}': 0.3, f'inst_b_{counter}': 0.3, f'inst_c_{counter}': 0.4}

    instantiation_influences = {
        f'inst_a_{counter}': 0, f'inst_b_{counter}': 0, f'inst_c_{counter}': 0}
    bn.add_context(context, instantiations)
    config['contexts'][context] = instantiations
    for intention in config['intentions']:
        config['intentions'][intention][context] = instantiation_influences
    assert default_to_regular(bn.config) == default_to_regular(config)


# @pytest.mark.timeout(N)
# def test_add_n_to_existing(n=N):
#     """
#     Test adding n contexts to an existing config
#     """
#     config = load_config('small_example.yml')
#     for i in range(n):
#         print('START')
#         test_add_to_existing(config=config, counter=i)
#         print(f'{config=}')

@pytest.mark.timeout(N)
def test_add_to_existing_loaded(config=None, counter=0):
    """
    Test adding a context to an existing config - with empty init and load
    """
    if config == None:
        config = load_config('small_example.yml')
    bn = BayesNet()
    bn.load('small_example.yml')

    context = f'the context_{counter}'
    instantiations = {
        f'inst_a_{counter}': 0.3, f'inst_b_{counter}': 0.3, f'inst_c_{counter}': 0.4}

    instantiation_influences = {
        f'inst_a_{counter}': 0, f'inst_b_{counter}': 0, f'inst_c_{counter}': 0}

    bn.add_context(context, instantiations)
    config['contexts'][context] = instantiations
    for intention in config['intentions']:
        config['intentions'][intention][context] = instantiation_influences
    assert default_to_regular(bn.config) == default_to_regular(config)
