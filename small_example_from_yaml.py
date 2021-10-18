'''
This is a small example with only some Intentions and Contexts that shows how this could work
'''
# %%
# System imports
import itertools
from collections import defaultdict

# 3rd party imports
import bnlearn as bn
from pgmpy.factors.discrete import TabularCPD
import numpy as np
import yaml
# local imports
from random_base_count import Counter

# end file header
__author__ = 'Adrian Lubitz'

# %%
# Load file
with open("small_example.yaml") as stream:
    content = yaml.safe_load(stream)

# Translation dicts for number of context as a card in bnlearn
value_to_card = defaultdict(dict)
for context, probabilities in content['contexts'].items():
    count = 0
    for key, val in probabilities.items():
        value_to_card[context][key] = count
        count += 1
print(value_to_card)
card_to_value = defaultdict(dict)
for intention, values in value_to_card.items():
    for name, num in values.items():
        card_to_value[intention][num] = name
print(card_to_value)
# Translation dict for the std values to probabilities
value_to_prob = {5: 0.95, 4: 0.75, 3: 0.5, 2: 0.25, 1: 0.05, 0: 0.0}

# initialize the bayesNet
contexts = list(content['contexts'].keys())
evidence = contexts
intentions = list(content['intentions'].keys())
print(intentions, contexts)
edges = list(itertools.product(contexts, intentions))
DAG = bn.make_DAG(edges)


# %%
# visualize Network
bn.plot(DAG)
# path = dot.render('test', directory='figures', format='svg', cleanup=True)

# %%
# Define probabilities for context
cpts = []
for context, probabilities in content['contexts'].items():
    # print(context, probabilities)
    values = [None] * len(probabilities)
    for value in probabilities:
        values[value_to_card[context][value]] = [probabilities[value]]
    # print(values)
    cpts.append(TabularCPD(
        variable=context, variable_card=len(probabilities), values=values)  # False, True
    )
# print (cpts)
# %%
# Define probabilities for intentions
for intention, context_influence in content['intentions'].items():
    # For every intention build the average of their influencing contexts
    evidence_card = []
    for evidence_variable in evidence:
        evidence_card.append(len(content['contexts'][evidence_variable]))
    pos_values = []
    for count in Counter(evidence_card):
        # Here I need to average over all the values that are in the yaml at position count
        average = 0
        for i in range(len(evidence_card)):
            average += value_to_prob[context_influence[evidence[i]
                                                       ][card_to_value[evidence[i]][count[i]]]]
        average /= len(evidence)
        pos_values.append(average)
    print(intention, pos_values)
    # create neg_values
    neg_values = [1-value for value in pos_values]
    print(neg_values)
    # create a TabularCPD with these Values(and automatic generated neg_values) and so on and add it into the cpts list
    cpts.append(TabularCPD(variable=intention, variable_card=2,  # intentions are always binary
                           # see https://pgmpy.org/factors/discrete.html?highlight=cpd#module-pgmpy.factors.discrete.CPD
                           values=[neg_values, pos_values],
                           evidence=evidence,
                           evidence_card=evidence_card))
# %%

DAG = bn.make_DAG(DAG, CPD=cpts)
# bn.print_CPD(DAG)

# %% save / Load
bn.bnlearn.save(DAG, filepath='bnlearn_model', overwrite=True)
DAG = bn.bnlearn.load(filepath='bnlearn_model')
# %%
# inference
evidence = {
    'speech commands': value_to_card['speech commands']['other'],
    'human holding object': value_to_card['human holding object'][True],
    'human activity': value_to_card['human activity']['working']
}
inference = {}
for intention in intentions:
    # only True values of binary intentions will be saved
    inference[intention] = bn.inference.fit(
        DAG, variables=[intention], evidence=evidence).values[1]
# normalize inference
normalized_inference = {}
probability_sum = sum(inference.values())
for intention, probability in inference.items():
    normalized_inference[intention] = inference[intention] / probability_sum

print(inference)
print(normalized_inference)

# %%

# %%
