'''
This module provides a class for a two-layer bayes net for context based intention recognition.
'''

# System imports
import itertools
from collections import defaultdict
from copy import deepcopy
import warnings


# 3rd party imports
import bnlearn as bn
from pgmpy.factors.discrete import TabularCPD
import numpy as np
import yaml
# local imports
from .random_base_count import Counter

# end file header
__author__ = 'Adrian Lubitz'


class BayesNet():
    def __init__(self, config=None, merge_config=False) -> None:
        '''
        Initializes the DAG with the given config
        '''
        self.valid = False

        self.discretization_functions = {}

        # config = deepcopy(config)
        config = config_to_default_dict(config)

        if not config:
            self.config = {'intentions': defaultdict(lambda: defaultdict(
                lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}
            return

        if not merge_config:
            # self.config = deepcopy(self.config_to_default_dict(config))
            self.config = deepcopy(config)
        else:
            # self.config = {**self.config, **
            #                deepcopy(self.config_to_default_dict(config))}
            self.config = {**self.config, **deepcopy(config)}

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
        # This is the config of the currently running BayesNet
        self.valid_config = deepcopy(self.config)
        self.valid = True

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

    def valid_evidence(self, context, instantiation):
        """
        returns true if evidence is a valid instantiation for the context 
        """
        try:
            if not instantiation in self.config['contexts'][context]:
                return False, f'{instantiation} is not a valid instantiation for {context}'
            else:
                return True, ''
        except:
            return False, ''

    def bind_discretization_function(self, context, discretization_function):
        """
        binds a discretization_function to a specific context.
        """
        if context not in self.contexts:
            raise ValueError(
                f'Cannot bind discretization function to {context}. Context does not exist!')
        self.discretization_functions[context] = discretization_function

    def infer(self, evidence, normalized=True):
        '''
        infers the probabilities for the intentions with given evidence
        evidence has the following form:
        evidence = {
            'speech commands': 'pickup',
            'human holding object': True,
            'human activity': 'idle'
        }
        '''
        # check if evidence values are in instantiations and create a card form of bnlearn

        card_evidence = {}
        for context, instantiation in evidence.items():
            valid, err_msg = self.valid_evidence(context, instantiation)
            if valid:
                card_evidence[context] = self.value_to_card[context][instantiation]
            elif context in self.discretization_functions:
                discrete_instantiation = self.discretization_functions[context](
                    instantiation)
                valid, err_msg = self.valid_evidence(
                    context, discrete_instantiation)
                if valid:
                    card_evidence[context] = self.value_to_card[context][discrete_instantiation]
                else:
                    raise ValueError(err_msg)

        if self.valid:
            inference = {}
            for intention in self.intentions:
                # only True values of binary intentions will be saved
                inference[intention] = bn.inference.fit(
                    self.DAG, variables=[intention], evidence=card_evidence).values[1]
            if normalized:
                return self.normalize_inference(inference)
            else:
                return inference
        else:
            raise Exception('Configuration is invalid')

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
        assert len(self.config['contexts']), 'No contexts defined'
        assert len(self.config['intentions']), 'No intentions defined'

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

    def create_zero_influence_dict(self, context_with_instantiations):
        """
        This is using the context with instantiations from the creation of a new context to set all values to zero
        It will have the following shape:
        {new_context:{
            inst_1:0,
            inst_2:0,
            ...
            inst_3:0
            }
        }
        """
        zeros = defaultdict(lambda: defaultdict(dict))
        for context, instantiations in context_with_instantiations.items():
            for instantiation, value in instantiations.items():
                zeros[context][instantiation] = 0
        return zeros

    def add_context(self, context, instantiations):
        """
        this will add a new context to the config and updates the bayesNet
        This call can crash if the config is not valid after the call
        """
        # check if context exists already
        if context in self.config['contexts']:
            raise ValueError(
                'Cannot add existing context - use edit_context to edit an existing context')
        # fill in the new context
        self.config['contexts'][context] = instantiations
        # add this context in every intention with instantiations and values beeing zero.
        # for intention in self.config['intentions']:
        #     self.config['intentions'][intention] = {**self.config['intentions'][intention], **self.create_zero_influence_dict(
        #         {context: instantiations})}
        self.transport_context_into_intentions()
        # reinizialize
        self.__init__(self.config, merge_config=False)

    def add_intention(self, intention):
        """
        this will add a new intention to the config and updates the bayesNet
        """
        # check if intention exists already
        if intention in self.config['intentions']:
            raise ValueError(
                'Cannot add existing intention - use edit_intention to edit an existing intention')
        # add in the intention filled with zeros for all contexts
        self.config['intentions'][intention] = defaultdict(
            lambda: defaultdict(int))
        self.transport_context_into_intentions()
        # for context, instantiations_with_values in self.config['contexts'].items():
        #     zeros = self.create_zero_influence_dict(
        #         {context: instantiations_with_values})
        #     self.config['intentions'][intention][context] = zeros[context]
        # reinizialize
        self.__init__(self.config, merge_config=False)

    def edit_context(self, context, instantiations, new_name=None):
        """
        Edits an existing context - this can also be used to remove instantiations
        Changing the name of an instantiation will always set the influence value of this instantiation to zero for all intentions!
        """
        # check if context exists already - only then I can edit
        if context not in self.config['contexts']:
            raise ValueError(
                'Cannot edit non existing context - use add_context to add a new context')
        if new_name:  # del old names context
            del(self.config['contexts'][context])
            # rename all occurences in intentions
            for intention in self.config['intentions']:
                old_instantiations = deepcopy(
                    self.config['intentions'][intention][context])
                del(self.config['intentions'][intention][context])
                self.config['intentions'][intention][new_name] = old_instantiations
            context = new_name

        self.config['contexts'][context] = instantiations
        self.remove_context_from_intentions()
        self.transport_context_into_intentions()
        # reinizialize
        self.__init__(self.config, merge_config=False)

    def edit_intention(self, intention, new_name):
        """
        Edits an existing intention
        """
        # check if context exists already - only then I can edit
        if intention not in self.config['intentions']:
            raise ValueError(
                'Cannot edit non existing intention - use add_intention to add a new intention')
        if new_name in self.config['intentions']:
            raise ValueError(
                f'{new_name} exists - cannot be given as the new name for {intention}')
        old_values = deepcopy(self.config['intentions'][intention])
        del(self.config['intentions'][intention])
        self.config['intentions'][new_name] = old_values
        # reinizialize
        self.__init__(self.config, merge_config=False)

    def del_context(self, context):
        """
        remove a context
        """
        del(self.config['contexts'][context])
        self.remove_context_from_intentions()
        self.transport_context_into_intentions()
        # reinizialize
        self.__init__(self.config, merge_config=False)

    def del_intention(self, intention):
        """
        remove a context
        """
        del(self.config['intentions'][intention])
        # reinizialize
        self.__init__(self.config, merge_config=False)

    def save(self, path, save_invalid=True):
        """
        saves the config of the bayesNet
        """
        if not self.valid and not save_invalid:
            raise ValueError(
                "saving invalid config is only possible if save_invalid is set to True")

        with open(path, 'w') as save_file:
            yaml.dump(default_to_regular(self.config), save_file)

    def load(self, path):
        """
        Loads a config and reinitializes the bayesNet
        """
        config = load_config(path)
        # reinizialize with config
        self.__init__(config)

    def change_context_apriori_value(self, context, instantiation, value):
        """
        Change the apriori_value for a context instantiation 
        """
        # check if this value already exists because I'm using defaultdict - otherwise you can just add values
        if instantiation in self.config['contexts'][context]:
            self.config['contexts'][context][instantiation] = value
            # reinizialize
            self.__init__(self.config, merge_config=False)
        else:
            raise ValueError(
                'change_context_apriori_value can only change values that exist already')

    def change_influence_value(self, intention, context, instantiation, value):
        """
        Change the influence value for a specific instatiation of a context for a specific intention.
        """
        # check if this value already exists because I'm using defaultdict - otherwise you can just add values
        if instantiation in self.config['intentions'][intention][context]:
            self.config['intentions'][intention][context][instantiation] = value
            self.__init__(self.config, merge_config=False)
        else:
            raise ValueError(
                'change_influence_value can only change values that exist already')

    def transport_context_into_intentions(self):
        """
        This checks if context is defined in the 'contexts' section of self.config which is not present in all intentions as influencing context. 
        Same for instantiations
        """
        for context in self.config['contexts']:
            for instantiation in self.config['contexts'][context]:
                for intention in self.config['intentions']:
                    if instantiation not in self.config['intentions'][intention][context]:
                        # This only works if it is a defaultdict
                        self.config['intentions'][intention][context][instantiation] = 0

    def remove_context_from_intentions(self):
        """
        This removes context or instantiations after removing/changing instantiations and/or context
        """
        # This is a hack because you can't edit while iterating a dict
        contexts_to_remove_from_intentions = []
        context_instantiations_to_remove_from_intentions = []
        for intention in self.config['intentions']:
            for context in self.config['intentions'][intention]:
                if context not in self.config['contexts']:
                    contexts_to_remove_from_intentions.append(
                        (intention, context))
                else:
                    for instantiation in self.config['intentions'][intention][context]:
                        if instantiation not in self.config['contexts'][context]:
                            context_instantiations_to_remove_from_intentions.append(
                                (intention, context, instantiation))
        for intention, context in contexts_to_remove_from_intentions:
            del(self.config['intentions'][intention][context])
        for intention, context, instantiation in context_instantiations_to_remove_from_intentions:
            del(self.config['intentions'][intention][context][instantiation])


def config_to_default_dict(config):
    if config == None:
        return None
    new_config = {'intentions': defaultdict(lambda: defaultdict(
        lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}
    for context in config['contexts']:
        for instantiation, value in config['contexts'][context].items():
            new_config['contexts'][context][instantiation] = value
    for intention in config['intentions']:
        # HERE: there is the chance that there is no context yet - write intention once
        new_config['intentions'][intention] = defaultdict(
            lambda: defaultdict(int))
        for context in config['intentions'][intention]:
            for instantiation, value in config['intentions'][intention][context].items():
                new_config['intentions'][intention][context][instantiation] = value
    return new_config


def load_config(path):
    with open(path) as stream:
        return config_to_default_dict(yaml.safe_load(stream))

# https://stackoverflow.com/questions/26496831/how-to-convert-defaultdict-of-defaultdicts-of-defaultdicts-to-dict-of-dicts-o


def default_to_regular(d):
    # transform dicts or default dicts because otherwise it will stop at the first dict and if that has another defaultdict in it - that won't transform
    if isinstance(d, defaultdict) or isinstance(d, dict):
        d = {k: default_to_regular(
            v) for k, v in d.items() if not isinstance(v, dict) or v}
    return d
