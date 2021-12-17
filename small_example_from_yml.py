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
with open("small_example.yml") as stream:
    config = yaml.safe_load(stream)
net = BayesNet(config)
# %%
# infer intentions with the given evidence
evidence = {
    'speech commands': net.value_to_card['speech commands']['pickup'],
    'human holding object': net.value_to_card['human holding object'][True],
    'human activity': net.value_to_card['human activity']['idle']
}
normalized_inference = net.infer(evidence)
print(normalized_inference)

# %%
