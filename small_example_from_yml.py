'''
This is a small example with only some Intentions and Contexts 
that shows how a bayes net for context based intention recognition 
is created from a config file.
'''
# %%
# System imports

# 3rd party imports

# local imports
from CoBaIR.bayes_net import BayesNet, load_config
from CoBaIR.default_discretizer import binary_decision

# end file header
__author__ = 'Adrian Lubitz'


# %%
# Load config from file

config = load_config("small_example.yml")
net = BayesNet(config)
# %%
# add combined influence value
net.add_combined_influence(
    'hand over tool', ('human activity', 'speech commands'), ('working', 'handover'), 5)
# %%
# del combined context influence
net.del_combined_influence(
    'pick up tool', ('speech commands', 'human holding object'), ('pickup', True))
# %%
# define discetazaion functio


def invalid_discretization_function(a):
    return "crap"


# %%
# bind discetazaion function
net.bind_discretization_function(
    'human holding object', lambda x: binary_decision(x, decision_boundary=0.7))
net.bind_discretization_function(
    'speech commands', invalid_discretization_function)  # this will only be triggered if the evidence for speech commands is invalid
# %%
# infer intentions with the given evidence
evidence = {
    'speech commands': 'pickup',
    'human holding object': 0.7,
    'human activity': 'idle',
    'invalid context': 'does not matter in evidence'
}
normalized_inference = net.infer(evidence)
print(normalized_inference)

# %%
