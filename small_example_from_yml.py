"""A small example with only some intentions and contexts.

It shows how the inference for context based intention recognition is created from a config file.
"""
# %%
# System imports

# 3rd party imports

# local imports
from cobair.default_discretizer import binary_decision
from cobair.infer import Inference
from cobair.model import Config

# end file header
__author__ = 'Adrian Lubitz'


# %%
# Load config from file
config = Config.load("small_example.yml")

# %%
# add combined influence value
config.add_combined_influence(
    'hand over tool', ('human activity', 'speech commands'), ('working', 'handover'), 5)
# %%
# del combined context influence
config.del_combined_influence(
    'pick up tool', ('speech commands', 'human activity'), ('pickup', 'working'))
# %%
# create the inference for the edited config
inference = Inference(config)

# %%
# define discretization function


def invalid_discretization_function(a):
    """Return an instantiation that doesn't exist."""
    return "crap"


# %%
# bind discretization function
inference.bind_discretization_function(
    'human holding object', lambda x: binary_decision(x, decision_boundary=0.7))
# this will only be triggered if the evidence for speech commands is invalid
inference.bind_discretization_function(
    'speech commands', invalid_discretization_function)
# %%
# infer intentions with the given evidence
evidence = {
    'speech commands': 'pickup',
    'human holding object': 0.7,
    'human activity': 'idle',
    'invalid context': 'does not matter in evidence'
}
max_intention, threshold, normalized_inference = inference.infer(
    evidence, decision_threshold=0.7)
print(normalized_inference)
print(max_intention)
print(threshold)
