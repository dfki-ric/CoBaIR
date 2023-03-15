'''
Tests for deleting intention variables
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


def test_delete_intention_from_empty():
    """
    Test deleting on a non existing config
    """
    bn = BayesNet()
    intention = "hand over tool"
    # I assume this will throw an Error!
    with pytest.raises(ValueError):
        bn.del_intention(intention)
    assert bn.config == config_to_default_dict()


def test_delete_intention_from_existing_intention():
    """
    Test deleting on an existing config - deleting the name of the intention
    """
    bn = BayesNet()
    bn.load('small_example.yml')
    old_config = deepcopy(bn.config)
    # cnt =0
    new_intention = list(bn.config['intentions'].keys())
    for intention in new_intention:
        if len(bn.config['intentions'].keys()) > 1:
            bn.del_intention(intention)
            assert intention not in bn.config['intentions']
        else:
            # while deleting the last context raises an Exception because there is no context
            with pytest.raises(AssertionError):
                bn.del_intention(intention)
                assert intention not in bn.config['intentions']
    assert bn.config != old_config


def test_delete_to_config_before_adding():
    """
    Test deleting a newly added intention to an existing config
    """
    bn = BayesNet()
    bn.load('small_example.yml')
    old_config = deepcopy(bn.config)
    new_intention = 'add new intention'
    bn.add_intention(new_intention)
    assert new_intention in bn.config['intentions']
    bn.del_intention(new_intention)
    assert new_intention not in bn.config['intentions']


def test_delete_config_before_edit():
    """
    Test deleting on an existing config - only changing the name of the intention
    """
    bn = BayesNet()
    bn.load('small_example.yml')
    new_name = 'entregar la herramienta'
    old_intention = 'hand over tool'
    bn.edit_intention(old_intention, new_name)
    assert new_name in bn.config['intentions']
    assert old_intention not in bn.config['intentions']
    bn.del_intention(new_name)
    assert new_name not in bn.config['intentions']
