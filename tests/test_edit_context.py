'''
Tests for adding intention variables
'''

# System imports
from copy import deepcopy
import pytest
# 3rd party imports

# local imports
from tests import N
from CoBaIR.bayes_net import BayesNet, default_to_regular, load_config

# end file header
__author__ = 'Adrian Lubitz'



def test_edit_context_from_empty():
    """
    Test editing on a non existing config
    """
    bn = BayesNet()
    old_config1 = deepcopy(bn.config)
    # I assume this will throw an Error!
    with pytest.raises(ValueError):
        bn.edit_context('the context', {
            'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4})
    assert old_config1 == bn.config

def test_edit_context_from_existing_new_name():
    """
    Test editing on an existing config - only changing the name of the context
    """
    bn = BayesNet()
    bn.load('small_example.yml')
    new_name = 'commandos de speechos'
    old_context = 'speech commands'
    old_config = deepcopy(bn.config)
    # I assume this will throw an Error!
    instantiations = deepcopy(bn.config['contexts'][old_context])
    bn.edit_context(old_context, instantiations, new_name=new_name)
    assert new_name in bn.config['contexts']
    assert old_context not in bn.config['contexts']
    assert instantiations == bn.config['contexts'][new_name]
    for intention in bn.config['intentions']:
        assert new_name in bn.config['intentions'][intention]
        assert old_context not in bn.config['intentions'][intention]
        assert old_config['intentions'][intention][old_context] == bn.config['intentions'][intention][new_name]

def test_edit_context_from_existing_new_instantiations():
    """
    Test editing on an existing config - changing the names and values of the instantiations
    """
    bn = BayesNet()
    bn.load('small_example.yml')
    context = 'speech commands'
    old_config = deepcopy(bn.config)
    # I assume this will throw an Error!
    instantiations = {
        'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4}
    bn.edit_context(context, instantiations)

    assert context in bn.config['contexts']
    assert instantiations == bn.config['contexts'][context]
    for intention in bn.config['intentions']:
        assert context in bn.config['intentions'][intention]
        # all influence values will be set to zero because I don't know if the instantiation is a total new or just corrected a typo
        for instantiation in instantiations:
            assert instantiation in bn.config['intentions'][intention][context]
            assert 0 == bn.config['intentions'][intention][context][instantiation]

def test_edit_context_from_existing_adjust_instantiations():
    """
    Test editing on an existing config - changing one name of the instantiations
    """
    bn = BayesNet()
    bn.load('small_example.yml')
    context = 'speech commands'
    old_config = deepcopy(bn.config)
    old_instantiation_name = 'pickup'
    new_instantiation_name = 'pick up'
    # I assume this will throw an Error!
    instantiations = deepcopy(bn.config['contexts'][context])
    old_value = instantiations[old_instantiation_name]
    del(instantiations[old_instantiation_name])
    instantiations[new_instantiation_name] = old_value
    bn.edit_context(context, instantiations)

    assert context in bn.config['contexts']
    assert instantiations == bn.config['contexts'][context]
    for intention in bn.config['intentions']:
        assert context in bn.config['intentions'][intention]
        # all influence values will be set to zero because I don't know if the instantiation is a total new or just corrected a typo
        for instantiation in instantiations:
            assert instantiation in bn.config['intentions'][intention][context]
            if instantiation != new_instantiation_name:
                assert old_config['intentions'][intention][context][instantiation] ==bn.config['intentions'][intention][context][instantiation]
            else:
                assert bn.config['intentions'][intention][context][instantiation] == 0

def test_edit_context_from_existing_new_instantiations_and_new_name():
    """
    Test editing on an existing config - changing the names and values of the instantiations and the context name
    """
    bn = BayesNet()
    bn.load('small_example.yml')
    new_name = 'commandos de speechos'
    old_context = 'speech commands'
    old_config = deepcopy(bn.config)
    # I assume this will throw an Error!
    instantiations = {
        'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4}
    bn.edit_context(old_context, instantiations, new_name=new_name)
    assert new_name in bn.config['contexts']
    assert instantiations == bn.config['contexts'][new_name]

    for intention in bn.config['intentions']:
        assert new_name in bn.config['intentions'][intention]
        # all influence values will be set to zero because I don't know if the instantiation is a total new or just corrected a typo
        for instantiation in instantiations:
            assert instantiation in bn.config['intentions'][intention][new_name]
            assert 0 == bn.config['intentions'][intention][new_name][instantiation]

def test_edit_context_from_existing_adjust_instantiations():
    """
    Test editing on an existing config - changing one name of the instantiations and the context name
    """
    bn = BayesNet()
    bn.load('small_example.yml')
    new_name = 'commandos de speechos'
    old_context = 'speech commands'
    old_config = deepcopy(bn.config)
    old_instantiation_name = 'pickup'
    new_instantiation_name = 'pick up'
    # I assume this will throw an Error!
    instantiations = deepcopy(bn.config['contexts'][old_context])
    old_value = instantiations[old_instantiation_name]
    del(instantiations[old_instantiation_name])
    instantiations[new_instantiation_name] = old_value
    bn.edit_context(old_context, instantiations, new_name=new_name)

    assert new_name in bn.config['contexts']
    assert instantiations == bn.config['contexts'][new_name]
    for intention in bn.config['intentions']:
        assert new_name in bn.config['intentions'][intention]
        # all influence values will be set to zero because I don't know if the instantiation is a total new or just corrected a typo
        for instantiation in instantiations:
            assert instantiation in bn.config['intentions'][intention][new_name]
            if instantiation != new_instantiation_name:
                assert old_config['intentions'][intention][old_context][instantiation] == bn.config['intentions'][intention][new_name][instantiation]
            else:
                assert bn.config['intentions'][intention][new_name][instantiation] == 0

