'''
This is a small example with only some Intentions and Contexts 
that shows how a bayes net for context based intention recognition 
is created from a config file.
'''
# %%
# System imports

# 3rd party imports
import yaml
# local imports
from CoBaBIR.bayes_net import BayesNet

# end file header
__author__ = 'Adrian Lubitz'


# %%
# Load config from file
with open("small_example_after_inference.yml") as stream:
    config = yaml.safe_load(stream)
net = BayesNet(config)
# %%
# define discetazaion function


def binary_decision(prob_value):
    if prob_value > 1.0 or prob_value < 0.0:
        raise ValueError(
            f'Probability values have to be in the range of [0.0, 1.0]. Given value is {prob_value}')
    if prob_value >= 0.5:
        return True
    else:
        return False


def invalid_discretization_function(a):
    return "crap"


# %%
# bind discetazaion function
net.bind_discretization_function('human holding object', binary_decision)
net.bind_discretization_function(
    'speech commands', invalid_discretization_function)  # this will only be triggered if the evidence for speech commands is invalid
# %%
# infer intentions with the given evidence
evidence = {
    'speech commands': 'pickup',
    'human holding object': 0.6,
    'human activity': 'idle',
    'invalid context': 'does not matter in evidence'
}
normalized_inference = net.infer(evidence)
print(normalized_inference)
