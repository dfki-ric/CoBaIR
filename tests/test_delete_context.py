'''
Tests for deleting context variables
'''

# System imports
from copy import deepcopy
import pytest

from collections import defaultdict
# 3rd party imports

# local imports
from tests import N
from CoBaIR.bayes_net import BayesNet, config_to_default_dict, default_to_regular, load_config

# end file header
__author__ = 'Arunima Gopikrishnan'


def test_delete_context_from_empty():
    """
    Test deleting on a non existing config
    """
    bn = BayesNet()
    context = "speech commands"
    # I assume this will throw an Error!
    with pytest.raises(ValueError):
        bn.del_context(context)
    assert bn.config == config_to_default_dict()


def test_delete_context_from_existing_context():
    """
    Test deleting on an existing config - deleting the name of the context and instantiations
    """
    bn = BayesNet()
    bn.load('small_example.yml')
    old_config = deepcopy(bn.config)
    # cnt =0
    new_contexts = list(bn.config['contexts'].keys())
    for context in new_contexts:
        if len(bn.config['contexts'].keys()) > 1:
            bn.del_context(context)
            assert context not in bn.config['contexts']
        else:
            # while deleting the last context raises an Exception because there is no context
            with pytest.raises(AssertionError):
                bn.del_context(context)
                assert context not in bn.config['contexts']
    assert bn.config != old_config


def test_delete_config_before_adding():
    """
    Test deleting a newly added context to an existing config
    """
    bn = BayesNet()
    bn.load('small_example.yml')
    old_config = deepcopy(bn.config)
    new_context = 'add new context'
    bn.add_context(new_context, {
        'inst_a': 0.2, 'inst_b': 0.3, 'inst_c': 0.5})
    assert new_context in bn.config['contexts']
    bn.del_context(new_context)
    assert new_context not in bn.config['contexts']


def test_delete_to_config_before_edit():
    """
    Test deleting on an existing config - only changing the name of the context
    """
    bn = BayesNet()
    bn.load('small_example.yml')
    new_name = 'commandos de speechos'
    old_context = 'speech commands'
    instantiations = deepcopy(bn.config['contexts'][old_context])
    bn.edit_context(old_context, instantiations, new_name)
    assert new_name in bn.config['contexts']
    assert old_context not in bn.config['contexts']
    bn.del_context(new_name)
    assert new_name not in bn.config['contexts']
