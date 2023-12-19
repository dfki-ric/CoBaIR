""" 
This module provides a class for a two-layer bayes net for context based intention recognition.
"""

# System imports
from __future__ import annotations
import itertools
from collections import defaultdict
from collections.abc import Hashable
from copy import deepcopy
import warnings
import logging

# 3rd party imports
import bnlearn as bn
from pgmpy.factors.discrete import TabularCPD
import yaml
# local imports
from .random_base_count import Counter

# end file header
__author__ = 'Adrian Lubitz'

# https://stackoverflow.com/questions/9169025/how-can-i-add-a-python-tuple-to-a-yaml-file-using-pyyaml


class PrettySafeLoader(yaml.SafeLoader):
    """A YAML loader that constructs Python tuples from YAML sequences."""

    def construct_python_tuple(self, node):
        """
        Construct a Python tuple from a YAML sequence node.

        Args:
            node (Any): The YAML sequence node to construct a tuple from.

        Returns:
            tuple: The constructed tuple.
        """
        return tuple(self.construct_sequence(node))


PrettySafeLoader.add_constructor(
    'tag:yaml.org,2002:python/tuple',
    PrettySafeLoader.construct_python_tuple)


class BayesNet():
    def __init__(self, config: dict = None, bn_verbosity: int = 0, validate: bool = True) -> None:
        '''
        Initializes the BayesNet with the given config.

        Args:
            config: A dict with a config following the config format.
            bn_verbosity: sets the verbose flag for bnlearn. See [bnlearn API](
                https://erdogant.github.io/bnlearn/pages/html/bnlearn.bnlearn.html?highlight=verbose
                #bnlearn.bnlearn.make_DAG) for more information
            validate: Flag if the given config should be validated or not. 
                This is necessary to load invalid configs
        '''
        self.log = logging.getLogger(self.__class__.__name__)

        self.valid = False
        self.bn_verbosity = bn_verbosity
        self.discretization_functions = {}

        if config is None:
            validate = False
        config = config_to_default_dict(config)

        # if not config:
        #     self.config = {'intentions': defaultdict(lambda: defaultdict(
        #         lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}
        #     return

        self.config = deepcopy(config)
        self.decision_threshold = self.config['decision_threshold']

        if validate:
            self.validate_config()

        # Translation dicts for context to card number in bnlearn and vice versa
        self._create_value_to_card()
        self._create_card_to_value()
        # Translation dict for the std values to probabilities
        self.value_to_prob = {5: 0.95, 4: 0.75,
                              3: 0.5, 2: 0.25, 1: 0.05, 0: 0.0}

        # initialize the bayes net structure
        self.contexts = self.evidence = list(self.config['contexts'].keys())
        self.intentions = list(self.config['intentions'].keys())
        self.edges = list(itertools.product(self.contexts, self.intentions))
        self._create_evidence_card()

        # create CPTs for the bayes net
        self.cpts = []
        self._create_context_cpts()
        self._create_intention_cpts()
        if self.valid:
            self.DAG = bn.make_DAG(self.edges, CPD=self.cpts,
                                   verbose=self.bn_verbosity)

    def _create_value_to_card(self):
        '''
        Initializes the translation dict for the context values to card numbers for bnlearn
        '''
        self.value_to_card = defaultdict(dict)
        for context, probabilities in self.config['contexts'].items():
            count = 0
            for key, _ in probabilities.items():
                self.value_to_card[context][key] = count
                count += 1

    def _create_card_to_value(self):
        '''
        Initializes the backtranslation dict for the context values to card numbers for bnlearn
        '''
        self.card_to_value = defaultdict(dict)
        for context, values in self.value_to_card.items():
            for name, num in values.items():
                self.card_to_value[context][num] = name

    def _create_context_cpts(self):
        '''
        Create the Conditional Probability Tables for all context nodes in the DAG and 
            APPENDS them to self.cpts
        '''
        for context, probabilities in self.config['contexts'].items():
            values = [None] * len(probabilities)
            for value in probabilities:
                values[self.value_to_card[context][value]] = [
                    probabilities[value]]
            self.cpts.append(TabularCPD(variable=context,
                             variable_card=len(probabilities), values=values))

    def _create_intention_cpts(self):
        '''
        Create the Conditional Probability Tables for all intention nodes in the DAG and 
            APPENDS them to self.cpts
        '''
        for intention, context_influence in self.config['intentions'].items():
            values = self._calculate_probability_values(context_influence)
            # create a TabularCPD
            self.cpts.append(
                TabularCPD(variable=intention,
                           variable_card=2,  # intentions are always binary
                           values=values,
                           evidence=self.evidence,
                           evidence_card=self.evidence_card)
            )

    def _create_evidence_card(self):
        '''
        create the evidence_card for bnlearn
        '''
        self.evidence_card = []
        for evidence_variable in self.evidence:
            self.evidence_card.append(
                len(self.config['contexts'][evidence_variable]))

    def _create_combined_context(self, context_influence: dict) -> dict:
        """
        Creates a dict with the combined contexts in card index format from context_influence.
        TODO: example makes no sense - replace
        Args:
            context_influence:
                A dict with the influence values for contexts.
                Example: {'speech commands':
                            {'pickup': 5, 'handover': 0, 'other': 0},
                          'human holding object':
                            {True: 1, False: 4},
                          'human activity':
                            {'idle': 4, 'working': 3}
                          }

        Returns:
            dict: A dict with the combined contexts
            Example: {(0, 2): {('pickup', 'working'): 5}), (0, 1): {('pickup', True): 5})}

        """
        combined_context = {}
        for context in context_influence:
            if isinstance(context, tuple):
                combined_context[tuple(map(self.evidence.index, context))
                                 ] = context_influence[context]
        return combined_context

    def _alter_combined_context(self, count: Counter, context_influence: dict,
                                combined_context: dict) -> dict:
        """
        Overwrites the influence values for the cases of combined influence.

        Args:
            count: 
                A counter that indicates for which combination of context the average is calculated
            context_influence: 
                A dict with the influence values for contexts.
                Example: {'speech commands':
                            {'pickup': 5, 'handover': 0, 'other': 0},
                          'human holding object':
                            {True: 1, False: 4},
                          'human activity':
                            {'idle': 4, 'working': 3}
                          }
            combined_context:
                A dict with the combined contexts
                Example: {(0, 2): {('pickup', 'working'): 5}), (0, 1): {('pickup', True): 5})}

        Returns:
            dict:
                A dict with the adjusted influence values for contexts.
                Example: {'speech commands':
                            {'pickup': 5, 'handover': 0, 'other': 0},
                          'human holding object':
                            {True: 5, False: 4},
                          'human activity':
                            {'idle': 4, 'working': 3}
                          }

        """
        active_case = list(
            map(lambda tup: self.card_to_value[self.evidence[tup[0]]][tup[1]], enumerate(count)))

        altered_context_influence = deepcopy(context_influence)

        for context_tuple, values in combined_context.items():
            combined_case = True
            # There should always be only one key
            value_tuple = list(values.keys())[0]
            for i, context_index in enumerate(context_tuple):
                if active_case[context_index] != value_tuple[i]:
                    combined_case = False
                    break
            if combined_case:
                for i, index in enumerate(context_tuple):
                    altered_context_influence[self.evidence[index]][value_tuple[i]] = \
                        combined_context[context_tuple][value_tuple]
                break
        return altered_context_influence

    def _calculate_probability_values(self, context_influence: dict) -> list:
        '''
        Calculates the probability values with the given context_influence from the config.

        Influence on the positive case(intention is true) is calculated as the
        average over all influences for the given context.
        The influence mapping is given in
        self.value_to_prob = {5: 0.95, 4: 0.75,
            3: 0.5, 2: 0.25, 1: 0.05, 0: 0.0}
        Args:
            context_influence:
                A dict with the influence values for contexts.
                Example: {'speech commands':
                            {'pickup': 5, 'handover': 0, 'other': 0},
                        'human holding object':
                            {True: 1, False: 4},
                        'human activity':
                            {'idle': 4, 'working': 3}
                        }
        Returns:
            list:
            A list of lists containing the probability values for the negative and positive.
            Example:

            [[0.416, 0.5, 0.183, 0.266, 0.733, 0.816, 0.5, 0.583, 0.733, 0.816, 0.5, 0.583],

            [0.583, 0.5, 0.816, 0.733, 0.266, 0.183, 0.5, 0.416, 0.266, 0.183, 0.5, 0.416]]
        '''
        # For every intention calculate the average of their influencing contexts
        pos_values = []
        combined_context = self._create_combined_context(context_influence)

        for count in Counter(self.evidence_card):
            # Here I need to average over all the values that are in the config at position count
            average = 0

            # alternate context_influence
            altered_context_influence = self._alter_combined_context(
                count, context_influence, combined_context)

            ####

            for i in range(len(self.evidence_card)):
                value = self.card_to_value[self.evidence[i]][count[i]]
                influence = altered_context_influence[self.evidence[i]][value]
                prob = self.value_to_prob.get(influence, 0)
                average += prob
            if len(self.evidence) > 0:
                average /= len(self.evidence)
            else:
                average = 0
            pos_values.append(average)
        # create neg_values
        neg_values = [1-value for value in pos_values]
        return [neg_values, pos_values]

    def valid_evidence(self, context: str, instantiation) -> tuple[bool, str]:
        """
        Tests if evidence is a valid instantiation for the context.

        Returns a bool if evidence is valid or not and a string with a error message if not valid.
        Args:
            context: a context
            instantiation: an instantiation of the context
        Returns:
            tuple[bool, str]:
            A tuple of bool to indicate validity and str for error/warn message
        """

        if context not in self.config['contexts']:
            # If context not known to the config is given in evidence it will just ignore that context.
            return True, f'Context "{context}" not set in config - will be ignored'

        if not isinstance(instantiation, Hashable):
            # I not hasable, it can't be used!
            return False, f'Context instatiations must be hashable! Instantiation "{instantiation}" for context "{context}" is not hashable!'

        if instantiation is None:
            # instantiation None is possible - in this case the apriori values will be used.
            return True, f'No instantiation given for context "{context}" - A prori values will be used.'

        if not instantiation in self.config['contexts'][context].keys():
            invalid_msg = f'"{instantiation}" is not a valid instantiation for "{context}". Using None instead'
            valid_options = list(self.config["contexts"][context].keys())
            valid_options_msg = f' Valid options are {valid_options}'
            return True, invalid_msg + valid_options_msg

        return True, ''

    def bind_discretization_function(self, context, discretization_function):
        """
        binds a discretization_function to a specific context.


        Args:
            context: One of the possible contexts from the config
            discretization_function: A discretization function which has to take one parameter and 
                return one of the possible discrete context instantiations.
        """
        if context not in self.contexts:
            raise ValueError(
                f'Cannot bind discretization function to {context}. Context does not exist!')
        self.discretization_functions[context] = discretization_function

    def infer(self, evidence, normalized=True, decision_threshold=None) -> tuple:
        '''
        infers the probabilities for the intentions with given evidence.

        Args:
            evidence:
                Evidence to infer the probabilities of all intentions.
                Evidence can contain context which is not in the config; 
                    it must not contain all possible contexts.
                Example:
                    {'speech commands': 'pickup',
                     'human holding object': True,
                     'human activity': 'idle'}
            decision_threshold: a threshold for picking the most likely intention. 
                Must be between 0 and 1. 
                If not given the decision_threshold defined on initialization is taken. 
            normalized: Flag if the returned inference is normalized to sum up to 1.
        Returns:
            tuple:
            Returns the highest ranking intention (or None if decision_threshold is not reached), the decision threshold
            and a dictionary of intentions and the corresponding probabilities.
        '''
        # check if evidence values are in instantiations and create a card form of bnlearn
        if decision_threshold is None:
            decision_threshold = self.config['decision_threshold']
        card_evidence = {}
        errors = []
        warning_msgs = []
        for context, instantiation in evidence.items():
            valid, err_msg = self.valid_evidence(context, instantiation)
            if valid:
                if err_msg:
                    warning_msgs.append(err_msg)
                    continue
                card_evidence[context] = self.value_to_card[context][instantiation]
            elif context in self.discretization_functions and instantiation is not None:
                discrete_instantiation = self.discretization_functions[context](
                    instantiation)
                valid, err_msg = self.valid_evidence(
                    context, discrete_instantiation)
                if valid:
                    if err_msg:
                        warning_msgs.append(err_msg)
                        continue
                    card_evidence[context] = self.value_to_card[context][discrete_instantiation]
                else:
                    errors.append(err_msg)
            else:
                errors.append(err_msg)

        if warning_msgs:
            for warning in warning_msgs:
                warnings.warn(warning)

        if errors:
            raise ValueError(f"{errors}")

        if self.valid:
            inference = {}
            for intention in self.intentions:
                # only True values of binary intentions will be saved
                inference[intention] = bn.inference.fit(
                    self.DAG,
                    variables=[intention],
                    evidence=card_evidence,
                    verbose=self.bn_verbosity
                ).values[1]

            if normalized:
                inference = self.normalize_inference(inference)
            max_intention = max(inference, key=inference.get)
            max_intention = max_intention if inference[max_intention] > decision_threshold else None
            return max_intention, decision_threshold, inference
        else:
            raise ValueError('Invalid configuration')

    def normalize_inference(self, inference: dict) -> dict:
        '''
        Normalizes the inference to a proper probability distribution.

        Inference which is not normalized will be normalized for one intention being True or False,
        which leads to uninterpretable results for inference of multiple intentions.

        Args:
            inference: dictionary of intentions and the corresponding probabilities
        Returns:
            dict: dictionary of intentions and the corresponding normalized probabilities.

        '''
        normalized_inference = {}
        probability_sum = sum(inference.values())
        for intention, probability in inference.items():
            normalized_inference[intention] = probability / probability_sum
        return normalized_inference

    def validate_config(self):
        '''
        validate that the current config follows the correct format.

        Raises:
            Warnings: Warning is raised if the config is not valid.

        Returns: 
            bool: True if config is valid, False otherwise
        '''
        # We assume the config is valid - if not this will be set to False - this allows to raise multiple warnings
        self.valid = True
        if 'contexts' not in self.config:
            warnings.warn('Field "contexts" must be defined in the config')
            self.valid = False
        if 'intentions' not in self.config:
            warnings.warn('Field "intentions" must be defined in the config')
            self.valid = False
        if not len(self.config['contexts']):
            warnings.warn('No contexts defined')
            self.valid = False
        if not len(self.config['intentions']):
            warnings.warn('No intentions defined')
            self.valid = False
        if not isinstance(self.config['decision_threshold'], float) or \
                not (0 <= self.config['decision_threshold'] < 1):
            warnings.warn(
                'Decision threshold must be a number between 0 and 1')
            self.valid = False

        # Intentions need to have influence value for all contexts and their possible instantiations
        for intention, context_influences in self.config['intentions'].items():
            for context, influences in context_influences.items():

                if isinstance(context, str) and context not in self.config['contexts']:
                    warnings.warn(
                        f'Context influence {context} cannot be found in the defined contexts!')
                    self.valid = False

                for instantiation, influence in influences.items():
                    if not isinstance(instantiation, tuple):
                        if not (0 <= influence <= 5 and isinstance(influence, int)):
                            warnings.warn(
                                f'Influence Value for {intention}.{context}.{instantiation} must be an integer between 0 and 5! Is {influence}')
                            self.valid = False
                        if instantiation not in self.config['contexts'][context].keys():
                            warnings.warn(
                                f'An influence needs to be defined for all instantiations! {intention}.{context}.{instantiation} does not fit the defined instantiations for {context}')
                            self.valid = False

        # Probabilities need to sum up to 1
        for context, instantiations in self.config['contexts'].items():
            for instantiation, value in instantiations.items():
                if not isinstance(value, float):
                    warnings.warn(
                        f'Apriori probability of context "{context}.{instantiation}" is not a number')
                    self.valid = False
            if sum(instantiations.values()) != 1.0:
                warnings.warn(
                    f'The sum of probabilities for context instantiations must be 1 - For "{context}" it is {sum(instantiations.values())}!')
                self.valid = False

        # This is the config of the currently running BayesNet
        if self.valid:
            self.valid_config = deepcopy(self.config)
        return self.valid

    def _create_zero_influence_dict(self, context_with_instantiations: dict) -> defaultdict:
        """
        This uses the context dict from config['contexts'] to instantiate a dict that can be used in 
            config['intentions']['some_context']

        Args:
            context_with_instantiations: 
                a dict holding contexts, their instantiations and corresponding apriori probabilities
        Returns:
            defaultdict:
            A dictionary with zero-initialized influence values for every given context.
            Example:
            {some_context:{
                inst_1:0,
                inst_2:0,
                ...
                inst_3:0
                }
            }
        """
        zeros = defaultdict(lambda: defaultdict(dict))
        for context, instantiations in context_with_instantiations.items():
            for instantiation, _ in instantiations.items():
                zeros[context][instantiation] = 0
        return zeros

    def add_context(self, context: str, instantiations: dict):
        """
        This will add a new context to the config and updates the bayesNet.

        Args:
            context: a new context for the config
            instantiations:
                a dict of the instantiations and their corresponding apriori probabilities
                Example:
                    {True: 0.6, False:0.4}
        Raises:
            ValueError: Raises a ValueError if the context already exists in the config
        """
        # check if context exists already
        if context in self.config['contexts']:
            raise ValueError(
                'Cannot add existing context - use edit_context to edit an existing context')
        # fill in the new context
        self.config['contexts'][context] = instantiations
        # add this context in every intention with instantiations and values beeing zero.
        self._transport_context_into_intentions()
        # reinizialize
        self.__init__(self.config)

    def add_intention(self, intention: str):
        """
        This will add a new intention to the config and updates the bayesNet.

        Args:
            intention: Name of a new intention

        Raises:
            ValueError: Raises a ValueError if the intention already exists in the config
        """
        # check if intention exists already
        if intention in self.config['intentions']:
            raise ValueError(
                'Cannot add existing intention - use edit_intention to edit an existing intention')
        # add in the intention filled with zeros for all contexts
        self.config['intentions'][intention] = defaultdict(
            lambda: defaultdict(int))
        self._transport_context_into_intentions()
        # for context, instantiations_with_values in self.config['contexts'].items():
        #     zeros = self._create_zero_influence_dict(
        #         {context: instantiations_with_values})
        #     self.config['intentions'][intention][context] = zeros[context]
        # reinizialize
        self.__init__(self.config)

    def edit_context(self, context: str, instantiations: dict, new_name: str = None):
        """
        Edits an existing context - this can also be used to remove instantiations

        !!! note
            Changing the name of an instantiation will always set the influence value of this 
                instantiation to zero for all intentions!

        Args:
            context: Name of the context to edit
            instantiations:
                A Dict of instantiations and their corresponding apriori probabilities.
                Example: {True: 0.6, False: 0.4}
            new_name: A new name for the context


        Raises:
            ValueError: Raises a ValueError if the context does not exists in the config
        """
        # check if context exists already - only then I can edit
        if context not in self.config['contexts']:
            raise ValueError(
                'Cannot edit non existing context - use add_context to add a new context')
        if new_name:  # del old names context
            del self.config['contexts'][context]
            # rename all occurences in intentions
            for intention in self.config['intentions']:
                old_instantiations = deepcopy(
                    self.config['intentions'][intention][context])
                del self.config['intentions'][intention][context]
                self.config['intentions'][intention][new_name] = old_instantiations
            context = new_name

        self.config['contexts'][context] = instantiations
        self._remove_context_from_intentions()
        self._transport_context_into_intentions()
        # reinizialize
        self.__init__(self.config)

    def edit_intention(self, intention: str, new_name: str):
        """
        Edits an existing intention.

        Args:
            intention: Name of the intention to edit
            new_name: A new name for the intention

        Raises:
            ValueError: Raises a ValueError if the intention does not exists in the config
        """
        # check if context exists already - only then I can edit
        if intention not in self.config['intentions']:
            raise ValueError(
                'Cannot edit non existing intention - use add_intention to add a new intention')
        if new_name in self.config['intentions']:
            raise ValueError(
                f'{new_name} exists - cannot be given as the new name for {intention}')
        old_values = deepcopy(self.config['intentions'][intention])
        del self.config['intentions'][intention]
        self.config['intentions'][new_name] = old_values
        # reinizialize
        self.__init__(self.config)

    def del_context(self, context: str):
        """
        Removes a context.

        Args:
            context: Name of the context to delete

        Raises:
            ValueError: An ValueError is raised if the context is not in self.config.
        """
        # Check if context exists already - only then I can edit
        if context not in self.config['contexts']:
            raise ValueError(
                'Cannot delete non-existing context - use add_context to add a new context')

        del self.config['contexts'][context]
        self._remove_context_from_intentions()
        self._transport_context_into_intentions()

        self.__init__(self.config)

    def del_intention(self, intention):
        """
        remove an intention.

        Args:
            intention: Name of the intention to delete

        Raises:
            ValueError: An ValueError is raised if the intention is not in self.config.
        """
        if intention not in self.config['intentions']:
            raise ValueError(
                'Cannot delete non existing intention - use add_intention to add a new intention')
        del self.config['intentions'][intention]
        # reinizialize
        self.__init__(self.config)

    def save(self, path: str, save_invalid: bool = True):
        """
        saves the config of the bayesNet to a yml file.

        Args:
            path: path to the file the config will be saved in
            save_invalid: Flag to decide if invalid configs can be saved
        Raises:
            ValueError: 
                A ValueError is raised if `save_invalid` is `False` and the config is not valid
        """
        if not self.valid and not save_invalid:
            warnings.warn("Invalid configuration will not be saved.")
        else:
            with open(path, 'w', encoding='utf-8') as save_file:
                yaml.dump(default_to_regular(self.config), save_file)

    def load(self, path: str):
        """
        Loads a config from file and reinitializes the bayesNet.

        Args:
            path: path to the file the config is saved in
        """
        config = load_config(path)
        # reinitialize with config
        self.__init__(config)

    def change_context_apriori_value(self, context: str, instantiation, value: float):
        """
        Changes the apriori_value for a context instantiation.

        Args:
            context: Name of the context
            instantiation: The instantiation for which the apriori value needs to be changed
            value: the new apriori value
        Raises:
            ValueError: Raises a ValueError if the instantiation does not exists in the config
        """
        # check if this value already exists because I'm using defaultdict
        # otherwise you can just add values
        if instantiation in self.config['contexts'][context]:
            self.config['contexts'][context][instantiation] = value
            # reinizialize
            self.__init__(self.config)
        else:
            raise ValueError(
                'change_context_apriori_value can only change values that exist already')

    def change_influence_value(self, intention: str, context: str, instantiation, value: int):
        """
        Update the influence value of a specific intention for a particular context instance..

        Args:
            intention: Name of the intention
            context: name of the context
            instantiation: The instantiation for which the influence value should be changed
            value: the new influence value. Can be one out of [0, 1, 2, 3, 4, 5]
        Raises:
            ValueError: Raises a ValueError if the instantiation does not exists in the config
        """
        # check if this value already exists because I'm using defaultdict
        # otherwise you can just add values
        if instantiation in self.config['intentions'][intention][context]:
            self.config['intentions'][intention][context][instantiation] = value
            self.__init__(self.config)
        else:
            raise ValueError(
                'change_influence_value can only change values that exist already')

    def add_combined_influence(self, intention: str, contexts: tuple,
                               instantiations: tuple, value: int):
        """
        Adds an influence value for a combination of context instantiations.

        Args:
            intention: Name of the intention
            contexts: tuple containing the names of the contexts
            instantiations: Tuple of context instances to set influence value for.
            value: influence value. Can be one out of [0, 1, 2, 3, 4, 5]
        Raises:
            ValueError: Raises a ValueError if the instantiation does not exists in the config
        """
        if not contexts:
            raise ValueError('Contexts list cannot be empty.')
        if intention not in self.config['intentions']:
            raise ValueError(
                f'"{intention}" does not exist in the list of intentions')
        for i, instantiation in enumerate(instantiations):
            if instantiation not in self.config['intentions'][intention][contexts[i]]:
                raise ValueError(
                    'add_combined_influence can only combine context instantiations that already exist')
        self.config['intentions'][intention][contexts][instantiations] = value
        self.__init__(self.config)

    def del_combined_influence(self, intention: str, contexts: tuple, instantiations: tuple):
        """
        Adds an influence value for a combination of context instantiations.

        Args:
            intention: Name of the intention
            contexts: tuple containing the names of the contexts
            instantiations: tuple of context instantiations
        Raises:
            ValueError: Raises a ValueError if the instantiation does not exists in the config
        """
        if instantiations not in self.config['intentions'][intention][contexts]:
            raise ValueError(
                'Combined context instantiations must exist to be removed.')
        del self.config['intentions'][intention][contexts]

    def _transport_context_into_intentions(self):
        """
        Transports contexts and their instantiations defined in the config['contexts'] into 
            config['intentions'] as influencing context if not present.
        """
        for context in self.config['contexts']:
            for instantiation in self.config['contexts'][context]:
                for intention in self.config['intentions']:
                    if instantiation not in self.config['intentions'][intention][context]:
                        # This only works if it is a defaultdict
                        self.config['intentions'][intention][context][instantiation] = 0

    def _remove_context_from_intentions(self):
        """
        This removes context or instantiation after removing/changing instantiations and/or context.
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
            del self.config['intentions'][intention][context]
        for intention, context, instantiation in context_instantiations_to_remove_from_intentions:
            del self.config['intentions'][intention][context][instantiation]

    def change_decision_threshold(self, decision_threshold):
        """
        Changes the decision threshold in the config.
        Args:
            decision_threshold: The new decision threshold.
        """
        self.config['decision_threshold'] = decision_threshold
        self.__init__(self.config)


def config_to_default_dict(config: dict = None):
    """
    This casts a config given as dict into a defaultdict.

    Args:
        config: A dict with a config following the config format.
    Returns:
        defaultdict:
            a defaultdict containing the config
    """
    if not config:
        config = {}
    new_config = {'intentions': defaultdict(lambda: defaultdict(
        lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}
    if 'contexts' in config:
        for context in config['contexts']:
            for instantiation, value in config['contexts'][context].items():
                new_config['contexts'][context][instantiation] = value
    if 'intentions' in config:
        for intention in config['intentions']:
            # HERE: there is the chance that there is no context yet - write intention once
            new_config['intentions'][intention] = defaultdict(
                lambda: defaultdict(int))
            for context in config['intentions'][intention]:
                for instantiation, value in config['intentions'][intention][context].items():
                    new_config['intentions'][intention][context][instantiation] = value
    if 'decision_threshold' in config:
        new_config['decision_threshold'] = config['decision_threshold']
    else:
        new_config['decision_threshold'] = 0.0

    return new_config


def load_config(path):
    """
    Helper function to load a config.

    Args:
        path: path to the file the config is saved in
    Returns:
        defaultdict:
            a defaultdict containing the config
    """

    # if os.path.splitext(path)[-1] != ".yml":
    #     raise TypeError(
    #         'Invalid format file - only supporting yml files')
    with open(path, encoding='utf-8') as stream:
        return config_to_default_dict(yaml.load(stream, Loader=PrettySafeLoader))


# https://stackoverflow.com/questions/26496831/how-to-convert-defaultdict-of-defaultdicts-of-defaultdicts-to-dict-of-dicts-o

def default_to_regular(d):
    """
    This casts a defaultdict to a regular dict which is needed for saving as yml file.

    Args:
        d: the dict which should be casted
    Returns:
        dict:
            a regular dict casted from the defaultdict
    """
    # casts dicts or default dicts because otherwise it will stop at the first dict and
    # if that has another defaultdict in it - that won't cast
    if isinstance(d, defaultdict) or isinstance(d, dict):
        d = {
            k: default_to_regular(v)
            for k, v in d.items()
            if not isinstance(v, dict) or v or isinstance(v, defaultdict)
        }
    return d
