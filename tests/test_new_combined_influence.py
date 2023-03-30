'''
Tests for new combined context influence
'''
# System imports
from copy import deepcopy
from collections import defaultdict
import pytest

# local imports
from CoBaIR.bayes_net import BayesNet

# end file header
__author__ = 'Arunima Gopikrishnan'

config = {'intentions': defaultdict(lambda: defaultdict(
        lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}

def test_new_combined_influence_into_empty():
    """
    Test adding combined context influence on a non existing config
    """
    bayes_net = BayesNet()
    intention = 'hand over tool'
    contexts =('speech commands','human activity')
    instantiations =('pickup','working')
    value = 5
    # I assume this will throw an Error!
    with pytest.raises(ValueError):
        bayes_net.add_combined_influence(intention, contexts, instantiations,value)


def test_change_influence_value_in_existing_new_combined_context_influence():
    """
    Test alter existing combined context influence from the loaded config's 
        existing combined context influence
    """
    bayes_net = BayesNet()
    bayes_net.load('small_example.yml')
    old_config = deepcopy(bayes_net.config)
    intention = 'pick up tool'
    contexts = ('speech commands','human activity')
    instantiations = ('pickup','working')
    value = 1
    bayes_net.add_combined_influence(intention, contexts, instantiations,value)
    assert intention in bayes_net.config['intentions']
    bayes_net.add_combined_influence(intention, contexts, instantiations,value)
    assert value not in bayes_net.config
    assert old_config != bayes_net.config

def test_new_combined_context_influence_from_existing_combined_context_influence():
    """
    Test adding combined context influence from the 
        loaded config's existing combined context influence
    """
    bayes_net = BayesNet()
    bayes_net.load('small_example.yml')
    original_config = bayes_net.config.copy()  # Make a copy of the original config

    for intention, context_influence in bayes_net.config['intentions'].items():
        bayes_net._create_combined_context(context_influence)

    intention = 'hand over tool'
    contexts = ('speech commands', 'human activity')
    instantiations = ('pickup', 'idle')
    value = 2
    bayes_net.add_combined_influence(intention, contexts, instantiations, value)

    assert bayes_net.config != original_config  # Compare the updated config to the original config

def test_create_combined_context():
    """
    Test creating combined context
    """
    bayes_net = BayesNet()
    bayes_net.load('small_example.yml')
    combined_context = "{(0, 2): defaultdict(<class 'int'>, {('pickup', 'working'): 5}),  \
                    (0, 1): defaultdict(<class 'int'>, {('pickup', True): 4})}"
    #combined = json.loads(combined_context)
    for context_influence in bayes_net.config['intentions'].items():
            bayes_net._calculate_probability_values(context_influence)
    data = bayes_net._create_combined_context(context_influence)
    assert combined_context == str(data)

def test_alter_combined_context():
    """
    Test alter existing combined context
    """
    bayes_net = BayesNet()
    bayes_net.load('small_example.yml')
    combined_context = "{(0, 2): defaultdict(<class 'int'>, {('pickup', 'working'): 5}), \
        (0, 1): defaultdict(<class 'int'>, {('pickup', True): 4})}"
    altered_combined_context = "{(0, 2): defaultdict(<class 'int'>, {('pickup', 'working'): 2}), (0, 1): defaultdict(<class 'int'>, {('pickup', True): 4})}"
    for context_influence in bayes_net.config['intentions'].items():
            bayes_net._calculate_probability_values(context_influence)
    data = bayes_net._create_combined_context(context_influence)
    assert combined_context == str(data)
    bayes_net = BayesNet()
    bayes_net.load('small_example_altered.yml')
    for context_influence in bayes_net.config['intentions'].items():
            bayes_net._calculate_probability_values(context_influence)
    data = bayes_net._create_combined_context(context_influence)
    assert altered_combined_context == str(data)

def test_calculate_probability_values():
    """
    Test calculating context probability values
    Influence value to probability = {5: 0.95, 4: 0.75, 3: 0.5, 2: 0.25, 1: 0.05, 0: 0.0}
    """
    bayes_net = BayesNet()
    bayes_net.load('small_example.yml')
    for context_influence in bayes_net.config['intentions'].items():
           (pos,neg) = bayes_net._calculate_probability_values(context_influence)
    print(pos,neg)
    bayes_net = BayesNet()
    bayes_net.load('small_example_altered.yml')
    for context_influence in bayes_net.config['intentions'].items():
           (alter_pos,alter_neg) = bayes_net._calculate_probability_values(context_influence)
    print(alter_pos,alter_neg)
    assert alter_pos != pos

    
