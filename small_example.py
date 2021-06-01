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
contexts = ['speech commands', 'hand opening degree', 'human activity']  # ,
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
# Define discretization functions

def discrete_hand_opening_degree(hand_opening_degree):
    '''
    this function transforms a hand opening degree into a discrete value of [closed=0, relaxed=1, wide-open=2]
    :param hand_opening_degree: A value from the hand opening degree prediction module - it is in the range 0-100%, where 0% is a completely closed hand and 100% would be a completely open hand.
    :type hand_opening_degree: float
    :returns: a discrete value of [closed=0, relaxed=1, wide-open=2]
    :rtype: int
    '''
    CLOSED = 0
    RELAXED = 1
    WIDE_OPEN = 2
    if hand_opening_degree < 25:
        return CLOSED
    elif hand_opening_degree > 75:
        return WIDE_OPEN
    else:
        return RELAXED


# %%
# Define probabilities
# P(hand opening degree)
cpt_hand_opening_degree = TabularCPD(
    variable='hand opening degree', variable_card=3, values=[[0.4], [0.4], [0.2]])  # closed, relaxed, wide-open
# print(cpt_human_holding_object)

# P(speech commands)
cpt_speech_commands = TabularCPD(variable='speech commands', variable_card=2, values=[
    [0.5], [0.5]])  # pickup, handover
# print(cpt_speech_commands)

# P(human activity)
cpt_human_activity = TabularCPD(
    variable='human activity', variable_card=2, values=[[0.2], [0.8]])  # idle, working
# print(cpt_human_activity)

# For True Class -> P(pick up tool[1]| hand opening degree[0], speech commands[0], human activity[0]), P(pick up tool[1]| hand opening degree[0], speech commands[0], human activity[1]), ... see http://pgmpy.org/factors.html#module-pgmpy.factors.discrete.CPD
cpt_pick_up_tool_pos = np.array(
    [0.90, 0.88, 0.15, 0.12, 0.99, 0.95, 0.15, 0.12, 0.95, 0.9, 0.12, 0.1])
#    000,  001,  010,  011,  100,  101,  110,  111,  200,  201, 210,  211
cpt_pick_up_tool_neg = 1 - cpt_pick_up_tool_pos
cpt_pick_up_tool = TabularCPD(variable='pick up tool', variable_card=2,  # False, True
                              values=[cpt_pick_up_tool_neg,
                                      cpt_pick_up_tool_pos
                                      ],
                              evidence=['hand opening degree',
                                        'speech commands', 'human activity'],
                              evidence_card=[3, 2, 2])
# print(cpt_pick_up_tool)

# For True Class -> P(handover_tool[1]| hand opening degree[0], speech commands[0], human activity[0]), P(handover_tool[1]| hand opening degree[0], speech commands[0], human activity[1]), ... see http://pgmpy.org/factors.html#module-pgmpy.factors.discrete.CPD
cpt_handover_tool_pos = np.array(
    [0.12, 0.1, 0.9, 0.88, 0.15, 0.12, 0.95, 0.9, 0.15, 0.12, 0.99, 0.95])
#    000,  001, 010, 011,  100,  101,  110,  111, 200,  201,  210,  211
cpt_handover_tool_neg = 1 - cpt_handover_tool_pos
cpt_handover_tool = TabularCPD(variable='hand over tool', variable_card=2,  # False, True
                               values=[cpt_handover_tool_neg,
                                       cpt_handover_tool_pos
                                       ],
                               evidence=['hand opening degree',
                                         'speech commands', 'human activity'],
                               evidence_card=[3, 2, 2])
# print(cpt_pick_up_tool)

DAG = bn.make_DAG(DAG, CPD=[cpt_hand_opening_degree, cpt_human_activity,
                  cpt_speech_commands, cpt_pick_up_tool, cpt_handover_tool])
# bn.print_CPD(DAG)
# %%
# inference
evidence = {
    'hand opening degree': discrete_hand_opening_degree(95.7),
    # 'speech commands': 1,
    'human activity': 0
}

q1 = bn.inference.fit(DAG, variables=['hand over tool'], evidence=evidence)
q2 = bn.inference.fit(DAG, variables=['pick up tool'], evidence=evidence)
# %%
