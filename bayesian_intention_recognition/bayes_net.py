'''
This module provides a class for a two-layer bayes net for context based intention recognition.
'''

# System imports
import itertools
from collections import defaultdict

# 3rd party imports
import bnlearn as bn
from pgmpy.factors.discrete import TabularCPD
import numpy as np
import yaml
# local imports
from bayesian_intention_recognition.random_base_count import Counter

# end file header
__author__ = 'Adrian Lubitz'


class BayesNet():
    def __init__(self, config) -> None:
        '''
        Initializes the DAG with the given config
        '''
        self.config = config
        self.validate_config()
        # Translation dicts for context to card number in bnlearn and vice versa
        self.create_value_to_card()
        self.create_card_to_value()
        # Translation dict for the std values to probabilities
        self.value_to_prob = {5: 0.95, 4: 0.75,
                              3: 0.5, 2: 0.25, 1: 0.05, 0: 0.0}

        # initialize the bayes net structure
        self.contexts = self.evidence = list(self.config['contexts'].keys())
        self.intentions = list(self.config['intentions'].keys())
        self.edges = list(itertools.product(self.contexts, self.intentions))
        self.create_evidence_card()

        # create CPTs for the bayes net
        self.cpts = []
        self.create_context_cpts()
        self.create_intention_cpts()
        self.DAG = bn.make_DAG(self.edges, CPD=self.cpts)

    def create_value_to_card(self):
        '''
        Initializes the translation dict for the context values to card numbers for bnlearn
        '''
        self.value_to_card = defaultdict(dict)
        for context, probabilities in self.config['contexts'].items():
            count = 0
            for key, val in probabilities.items():
                self.value_to_card[context][key] = count
                count += 1

    def create_card_to_value(self):
        '''
        Initializes the backtranslation dict for the context values to card numbers for bnlearn
        '''
        self.card_to_value = defaultdict(dict)
        for intention, values in self.value_to_card.items():
            for name, num in values.items():
                self.card_to_value[intention][num] = name

    def create_context_cpts(self):
        '''
        Create the Conditional Probability Tables for all context nodes in the DAG and APPENDS them to self.cpts
        '''
        for context, probabilities in self.config['contexts'].items():
            values = [None] * len(probabilities)
            for value in probabilities:
                values[self.value_to_card[context][value]] = [
                    probabilities[value]]
            self.cpts.append(TabularCPD(variable=context,
                             variable_card=len(probabilities), values=values))

    def create_intention_cpts(self):
        '''
        Create the Conditional Probability Tables for all intention nodes in the DAG and APPENDS them to self.cpts
        '''
        for intention, context_influence in self.config['intentions'].items():
            values = self.calculate_probability_values(context_influence)
            # create a TabularCPD
            self.cpts.append(TabularCPD(variable=intention, variable_card=2,  # intentions are always binary
                                        # see https://pgmpy.org/factors/discrete.html?highlight=cpd#module-pgmpy.factors.discrete.CPD
                                        values=values,
                                        evidence=self.evidence,
                                        evidence_card=self.evidence_card))

    def create_evidence_card(self):
        '''
        create the evidence_card for bnlearn
        '''
        self.evidence_card = []
        for evidence_variable in self.evidence:
            self.evidence_card.append(
                len(self.config['contexts'][evidence_variable]))

    def calculate_probability_values(self, context_influence):
        '''
        Calculates the probability values with the given context_influence from the config.
        Influence on the positive case(intention is true) is calculated as the average over all influences for the given context.
        '''
        # For every intention calculate the average of their influencing contexts
        pos_values = []
        for count in Counter(self.evidence_card):
            # Here I need to average over all the values that are in the config at position count
            average = 0
            for i in range(len(self.evidence_card)):
                average += self.value_to_prob[context_influence[self.evidence[i]
                                                                ][self.card_to_value[self.evidence[i]][count[i]]]]
            average /= len(self.evidence)
            pos_values.append(average)
        # create neg_values
        neg_values = [1-value for value in pos_values]
        return [neg_values, pos_values]

    def infer(self, evidence, normalized=True):
        '''
        infers the probabilities for the intentions with given evidence
        '''
        # TODO: evidence should be plain values and not cards. translation to cards and discretazation should be done internally
        inference = {}
        for intention in self.intentions:
            # only True values of binary intentions will be saved
            inference[intention] = bn.inference.fit(
                self.DAG, variables=[intention], evidence=evidence).values[1]
        if normalized:
            return self.normalize_inference(inference)
        else:
            return inference

    def normalize_inference(self, inference):
        '''
        Normalizes the inference to a proper probability distribution
        '''
        normalized_inference = {}
        probability_sum = sum(inference.values())
        for intention, probability in inference.items():
            normalized_inference[intention] = probability / probability_sum
        return normalized_inference

    def validate_config(self):
        '''
        validate that the config follows the correct format
        '''
        # contexts and intentions need to be defined
        assert 'contexts' in self.config, 'Field "contexts" must be defined in the config'
        assert 'intentions' in self.config, 'Field "intentions" must be defined in the config'

        # Intentions need to have influence values for all contexts and their possible instantiations
        for intention, context_influences in self.config['intentions'].items():
            for context, influences in context_influences.items():
                assert context in self.config[
                    'contexts'], f'Context influence {context} cannot be found in the defined contexts!'
                assert influences.keys() == self.config['contexts'][context].keys(
                ), f'An influence needs to be defined for all instantiations! {intention}.{context} does not fit the defined instantiations for {context}'
                for instantiation, influence in influences.items():
                    assert 5 >= influence >= 0 and isinstance(
                        influence, int), f'Influence Value for {intention}.{context}.{instantiation} must be an integer between 0 and 5! Is {influence}'
        # Probabilities need to sum up to 1
        for context, instantiations in self.config['contexts'].items():
            assert sum(instantiations.values(
            )) == 1.0, f'The sum of probabilities for context instantiations must be 1 - For {context} it is {sum(instantiations.values())}!'


if __name__ == '__main__':
    with open("../small_example.yaml") as stream:
        config = yaml.safe_load(stream)
    net = BayesNet(config)
    evidence = {
        'speech commands': net.value_to_card['speech commands']['other'],
        'human holding object': net.value_to_card['human holding object'][True],
        'human activity': net.value_to_card['human activity']['working']
    }
    normalized_inference = net.infer(evidence)
    print(normalized_inference)
