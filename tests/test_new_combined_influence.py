'''
Tests for new combined context influence
'''

# System imports
from copy import deepcopy
from matplotlib.style import context
import pytest

from collections import defaultdict

# local imports
from tests import N
from CoBaIR.bayes_net import BayesNet, default_to_regular, load_config

# end file header
__author__ = 'Arunima Gopikrishnan'

config = {'intentions': defaultdict(lambda: defaultdict(
        lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}
def test_new_combined_influence_into_empty():
    """
    Test adding combined context influence on a non existing config
    """
    bn = BayesNet()
    intention = 'hand over tool'
    contexts =('speech commands','human activity')
    instantiations =('pickup','working')
    value = 5
    # I assume this will throw an Error!
    with pytest.raises(ValueError):
        bn.add_combined_influence(intention, contexts, instantiations,value)


def test_change_influence_value_in_existing_new_combined_context_influence():
    """
    Test alter existing combined context influence from the loaded config's existing combined context influence
    """
    
    bn = BayesNet()
    bn.load('small_example.yml')
    old_config = deepcopy(bn.config)
 #   for intention, context_influence in bn.config['intentions'].items():
#            bn._create_combined_context(context_influence)
    intention = 'pick up tool'
    contexts = ('speech commands','human activity')
    instantiations = ('pickup','working')
    value = 1
    bn.add_combined_influence(intention, contexts, instantiations,value)
    assert intention in bn.config['intentions']
    bn.add_combined_influence(intention, contexts, instantiations,value)
    assert value not in bn.config
    assert old_config != bn.config


def test_new_combined_context_influence_from_existing_combined_context_influence():
    """
    Test adding combined context influence from the loaded config's existing combined context influence
    """
    
    bn = BayesNet()
    bn.load('small_example.yml')
    for intention, context_influence in bn.config['intentions'].items():
        bn._create_combined_context(context_influence)
    intention = 'hand over tool'
    contexts = ('speech commands','human activity')
    instantiations = ('pickup','idle')
    value=2
    bn.add_combined_influence(intention, contexts, instantiations,value)
    assert context_influence != bn.config
    

def test_create_combined_context():
    """
    Test creating combined context
    """
    
    bn = BayesNet()
    bn.load('small_example.yml')
    combined_context = "{(0, 2): defaultdict(<class 'int'>, {('pickup', 'working'): 5}), (0, 1): defaultdict(<class 'int'>, {('pickup', True): 4})}"
    #combined = json.loads(combined_context)
    #combined_context = "{(0, 1): defaultdict(<class 'int'>, {('pickup', True): 4}), (0, 2): defaultdict(<class 'int'>, {('pickup', 'working'): 5})}"
    for intention, context_influence in bn.config['intentions'].items():
            bn._calculate_probability_values(context_influence)
    data = bn._create_combined_context(context_influence)
    assert combined_context == str(data)


def test_alter_combined_context():
    """
    Test alter existing combined context
    """
        
    bn = BayesNet()
    bn.load('small_example.yml')
    combined_context = "{(0, 2): defaultdict(<class 'int'>, {('pickup', 'working'): 5}), (0, 1): defaultdict(<class 'int'>, {('pickup', True): 4})}"
    altered_combined_context = "{(0, 2): defaultdict(<class 'int'>, {('pickup', 'working'): 2}), (0, 1): defaultdict(<class 'int'>, {('pickup', True): 4})}"
    for intention, context_influence in bn.config['intentions'].items():
            bn._calculate_probability_values(context_influence)
    data = bn._create_combined_context(context_influence)
   # data = bn._calculate_probability_values(defaultdict(<function config_to_default_dict.<locals>.<lambda> at 0x0000017F41ED0A60>, {'speech commands': defaultdict(<class 'int'>, {'handover': 0, 'other': 0, 'pickup': 5}), 'human holding object': defaultdict(<class 'int'>, {False: 4, True: 1}), ('speech commands', 'human activity'): defaultdict(<class 'int'>, {('pickup', 'working'): 5}), 'human activity': defaultdict(<class 'int'>, {'idle': 4, 'working': 3}), ('speech commands', 'human holding object'): defaultdict(<class 'int'>, {('pickup', True): 4})}))
    assert combined_context == str(data)
    bn = BayesNet()
    bn.load('small_example_altered.yml')
    for intention, context_influence in bn.config['intentions'].items():
            bn._calculate_probability_values(context_influence)
    data = bn._create_combined_context(context_influence)
    assert altered_combined_context == str(data)


    
def test_calculate_probability_values():
    """
    Test calculating context probability values
    Influence value to probability = {5: 0.95, 4: 0.75, 3: 0.5, 2: 0.25, 1: 0.05, 0: 0.0}
    """
    
    bn = BayesNet()
    bn.load('small_example.yml')
    for intention, context_influence in bn.config['intentions'].items():
           (pos,neg) = bn._calculate_probability_values(context_influence)
    print(pos,neg)
    bn = BayesNet()
    bn.load('small_example_altered.yml')
    for intention, context_influence in bn.config['intentions'].items():
           (alter_pos,alter_neg) = bn._calculate_probability_values(context_influence)
    print(alter_pos,alter_neg)
    assert alter_pos != pos

    
