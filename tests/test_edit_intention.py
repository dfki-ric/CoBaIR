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
__author__ = 'Arunima Gopikrishnan'

def test_edit_intention_from_empty():
    """
    Test editing on a non existing config
    """
    bn = BayesNet()
    old_config1 = deepcopy(bn.config)
    intention = 'hand over tool'
    new_name = 'entregar la herramienta'
    # I assume this will throw an Error!
    with pytest.raises(ValueError):
        bn.edit_intention(intention, new_name=new_name)
    assert old_config1 == bn.config

def test_edit_intention_from_existing_new_name():
    """
    Test editing on an existing config - only changing the name of the intention
    """
    bn = BayesNet()
    bn.load('small_example.yml')
    new_name = 'entregar la herramienta'
    old_intention = 'hand over tool'
    old_config = deepcopy(bn.config)
    # I assume this will throw an Error! 
    bn.edit_intention(old_intention, new_name=new_name)
    assert new_name in bn.config['intentions']
    assert old_intention not in bn.config['intentions']



