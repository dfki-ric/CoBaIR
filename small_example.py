'''
This is a small example with only some Intentions and Contexts that shows how this could work
'''
# %%
# System imports
import itertools

# 3rd party imports
import bnlearn as bn
from pgmpy.factors.discrete import TabularCPD
import numpy as np
# local imports

# end file header
__author__ = 'Adrian Lubitz'

# %%
# Construct Network
contexts = ['speech commands', 'human holding object', 'human activity']  # ,
# 'robot activity', 'object 6D']
intentions = ['pick up tool', 'hand over tool']

edges = list(itertools.product(contexts, intentions))

print(edges)
DAG = bn.make_DAG(edges)


# %%
# visualize Network
bn.plot(DAG)
# path = dot.render('test', directory='figures', format='svg', cleanup=True)

# %%
# Define probabilities


# P(human holding object)
cpt_human_holding_object = TabularCPD(
    variable='human holding object', variable_card=2, values=[[0.6], [0.4]])  # False, True
# print(cpt_human_holding_object)

# P(speech commands)
cpt_speech_commands = TabularCPD(variable='speech commands', variable_card=3, values=[
    [0.2], [0.2], [0.6]])  # pickup, handover, other
# print(cpt_speech_commands)

# P(human activity)
cpt_human_activity = TabularCPD(
    variable='human activity', variable_card=2, values=[[0.2], [0.8]])  # idle, working
# print(cpt_human_activity)

cpt_pick_up_tool = TabularCPD(variable='pick up tool', variable_card=2,  # False, True
                              values=[np.add([0.01, 0.12, 0.85, 0.88, 0.85, 0.88, 0.1, 0.15, 0.88, 0.9, 0.88, 0.9], 0.0).tolist(),
                                      # P(pick up tool[0]| human holding object[0], speech commands[0]), P(pick up tool[0]| human holding object[0], speech commands[1]), P(pick up tool[0]| human holding object[0], speech commands[2]), ... see http://pgmpy.org/factors.html#module-pgmpy.factors.discrete.CPD
                                      np.add([0.99, 0.88, 0.15, 0.12, 0.15, 0.12,
                                              0.9, 0.85, 0.12, 0.1, 0.12, 0.1], 0.0).tolist(),
                                      ],
                              evidence=['human holding object',
                                        'speech commands', 'human activity'],
                              evidence_card=[2, 3, 2])
# print(cpt_pick_up_tool)

cpt_handover_tool = TabularCPD(variable='hand over tool', variable_card=2,  # False, True
                               values=[np.add([0.85, 0.88, 0.01, 0.12, 0.85, 0.88, 0.88, 0.9, 0.1, 0.15, 0.88, 0.9], 0.03).tolist(),
                                       # P(pick up tool[0]| human holding object[0], speech commands[0]), P(pick up tool[0]| human holding object[0], speech commands[1]), P(pick up tool[0]| human holding object[0], speech commands[2]), ... see http://pgmpy.org/factors.html#module-pgmpy.factors.discrete.CPD
                                       np.add([0.15, 0.12, 0.99, 0.88, 0.15, 0.12,
                                               0.12, 0.1, 0.9, 0.85, 0.12, 0.1], -0.03).tolist(),
                                       ],
                               evidence=['human holding object',
                                         'speech commands', 'human activity'],
                               evidence_card=[2, 3, 2])
# print(cpt_pick_up_tool)

DAG = bn.make_DAG(DAG, CPD=[cpt_human_holding_object, cpt_human_activity,
                  cpt_speech_commands, cpt_pick_up_tool, cpt_handover_tool])
# bn.print_CPD(DAG)
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
