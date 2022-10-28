'''
Tests for remove combined context influence
'''

# System imports
from copy import deepcopy
import pytest

from collections import defaultdict

# local imports
from tests import N
from CoBaIR.bayes_net import BayesNet, default_to_regular, load_config

# end file header
__author__ = 'Arunima Gopikrishnan'

config = {'intentions': defaultdict(lambda: defaultdict(
        lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}
def test_remove_combined_influence_from_empty():
    """
    Test removing combined context influence on a non existing config
    """
    bn = BayesNet()
    contexts = 'hand over tool'
    intention = ('speech commands','human activity')
    instantiations = ('pickup','working')
    # I assume this will throw an Error!
    with pytest.raises(ValueError):
        bn.del_combined_influence(intention, contexts, instantiations)



def test_remove_existing_add_new_combined_context_influence():
    """
    Test removing combined context influence from the loaded config's existing combined context influence
    and adding combined context influence into the loaded config's existing combined context influence
    """
    
    bn = BayesNet()
    bn.load('small_example.yml')
    original_config = deepcopy(bn.config)
 #   for intention, context_influence in bn.config['intentions'].items():
#            bn._create_combined_context(context_influence)
    intention = 'pick up tool'
    contexts = ('speech commands','human activity')
    instantiations = ('pickup','working')
    value = 5
    bn.del_combined_influence(intention, contexts, instantiations)
    altered_config = deepcopy(bn.config)
    assert altered_config != original_config
    bn.add_combined_influence(intention, contexts, instantiations,value)
    assert original_config == bn.config
    
