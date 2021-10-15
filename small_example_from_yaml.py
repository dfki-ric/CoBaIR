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
intentions = content['intentions'].keys()
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
        pos_values.insert(0, average)
    print(intention, pos_values)
    # TODO: check the ordering of the values!! + create a TabularCPD with these Values(and automatic generated neg_values) and so on and add it into the cpts list
# %%

# cpt_pick_up_tool = TabularCPD(variable='pick up tool', variable_card=2,  # False, True
#                               values=[np.add([0.01, 0.12, 0.85, 0.88, 0.85, 0.88, 0.1, 0.15, 0.88, 0.9, 0.88, 0.9], 0.0).tolist(),  # These are False values and the can be computed from true values because intentions are binary
#                                       # P(pick up tool[0]| human holding object[0], speech commands[0]), P(pick up tool[0]| human holding object[0], speech commands[1]), P(pick up tool[0]| human holding object[0], speech commands[2]), ... see https://pgmpy.org/factors/discrete.html?highlight=cpd#module-pgmpy.factors.discrete.CPD
#                                       np.add([0.99, 0.88, 0.15, 0.12, 0.15, 0.12,
#                                               0.9, 0.85, 0.12, 0.1, 0.12, 0.1], 0.0).tolist(),
#                                       ],
#                               evidence=evidence,
#                               evidence_card=evidence_card)
# # print(cpt_pick_up_tool)

# cpt_handover_tool = TabularCPD(variable='hand over tool', variable_card=2,  # False, True
#                                values=[np.add([0.85, 0.88, 0.01, 0.12, 0.85, 0.88, 0.88, 0.9, 0.1, 0.15, 0.88, 0.9], 0.03).tolist(),
#                                        # P(pick up tool[0]| human holding object[0], speech commands[0]), P(pick up tool[0]| human holding object[0], speech commands[1]), P(pick up tool[0]| human holding object[0], speech commands[2]), ... see http://pgmpy.org/factors.html#module-pgmpy.factors.discrete.CPD
#                                        np.add([0.15, 0.12, 0.99, 0.88, 0.15, 0.12,
#                                                0.12, 0.1, 0.9, 0.85, 0.12, 0.1], -0.03).tolist(),
#                                        ],
#                                evidence=['human holding object',
#                                          'speech commands', 'human activity'],
#                                evidence_card=[2, 3, 2])
# # print(cpt_pick_up_tool)

DAG = bn.make_DAG(DAG, CPD=[cpt_human_holding_object, cpt_human_activity,
                            cpt_speech_commands, cpt_pick_up_tool, cpt_handover_tool])
# bn.print_CPD(DAG)

# %% save / Load
bn.bnlearn.save(DAG, filepath='bnlearn_model', overwrite=True)
DAG = bn.bnlearn.load(filepath='bnlearn_model')
# %%
# inference
evidence = {
    'human holding object': 1,
    # 'speech commands': 2,
    'human activity': 0
}

q1 = bn.inference.fit(DAG, variables=['hand over tool'], evidence=evidence)
q2 = bn.inference.fit(DAG, variables=['pick up tool'], evidence=evidence)
# %%
