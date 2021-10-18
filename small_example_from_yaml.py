'''
This is a small example with only some Intentions and Contexts 
that shows how a bayes net for context based intention recognition 
is created from a config file.
'''

# System imports

# 3rd party imports
import yaml
# local imports
from bayesian_intention_recognition.bayes_net import BayesNet

# end file header
__author__ = 'Adrian Lubitz'

if __name__ == '__main__':
    with open("small_example.yaml") as stream:
        config = yaml.safe_load(stream)
    net = BayesNet(config)
    evidence = {
        'speech commands': net.value_to_card['speech commands']['other'],
        'human holding object': net.value_to_card['human holding object'][True],
        'human activity': net.value_to_card['human activity']['working']
    }
    normalized_inference = net.infer(evidence)
    print(normalized_inference)
