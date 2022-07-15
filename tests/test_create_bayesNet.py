'''
Tests for adding intention variables
'''

# System imports
import pytest

# 3rd party imports

# local imports
from tests import N
from CoBaIR.bayes_net import BayesNet, load_config

# end file header
__author__ = 'Adrian Lubitz'



def test_context_intention_from_empty():
    """
    Test adding a context and following an intention to an empty config
    """
    bn = BayesNet()
    # I assume this will throw an Error!
    with pytest.raises(AssertionError):
        bn.add_context('the context', {
            'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4})
    bn.add_intention('some intention')

def test_n_context_intention_from_empty(n=N):
    """
    Test adding n contexts and following an intention to an empty config
    """
    context = 'context'
    instantiations = {
        'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4}
    bn = BayesNet()
    for i in range(n):
        # I assume this will throw an Error!
        with pytest.raises(AssertionError):
            bn.add_context(f'{context}_{i}', instantiations)
    bn.add_intention('some intention')

def test_intention_context_from_empty():
    """
    Test adding an intention and following a context to an empty config
    """
    bn = BayesNet()
    # I assume this will throw an Error!
    with pytest.raises(AssertionError):
        bn.add_intention('some intention')
    bn.add_context('the context', {
        'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4})

def test_n_intention_context_from_empty(n=N):
    """
    Test adding n intentions and following a context to an empty config
    """
    intention = 'intention'

    bn = BayesNet()
    for i in range(n):
        # I assume this will throw an Error!
        with pytest.raises(AssertionError):
            bn.add_intention(f'{intention}_{i}')
    bn.add_context('the context', {
        'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4})

def test_load_from_existing():
    """
    Test if loading a new config overwrites the old
    """
    bn = BayesNet()
    # I assume this will throw an Error!
    with pytest.raises(AssertionError):
        bn.add_context('the context', {
            'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4})
    bn.add_intention('some intention')
    bn.load('small_example.yml')
    # Assert that it overwrites
    assert bn.config == load_config('small_example.yml')

def test_load_and_save():
    """
    Testing if loaded and saved configs are equal.
    """
    bn = BayesNet()
    bn.load('small_example.yml')
    bn.save('small_example_copy.yml')
    assert load_config('small_example.yml') == load_config('small_example_copy.yml')


