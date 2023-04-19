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
    bayes_net = BayesNet()
    old_config1 = deepcopy(bayes_net.config)
    intention = 'hand over tool'
    new_name = 'entregar la herramienta'
    # I assume this will throw an Error!
    with pytest.raises(ValueError):
        bayes_net.edit_intention(intention, new_name=new_name)
    assert old_config1 == bayes_net.config

def test_edit_intention_from_existing_new_name():
    """
    Test editing on an existing config - only changing the name of the intention
    """
    bayes_net = BayesNet()
    bayes_net.load('small_example.yml')
    new_name = 'entregar la herramienta'
    old_intention = 'hand over tool'
    # I assume this will throw an Error!
    bayes_net.edit_intention(old_intention, new_name=new_name)
    assert new_name in bayes_net.config['intentions']
    assert old_intention not in bayes_net.config['intentions']