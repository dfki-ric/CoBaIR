"""Deprecated 4.x API, use `cobair.model` and `cobair.infer` instead. Removed in 6.0.0.

| 4.x | 5.x |
|---|---|
| `BayesNet(config)` | `Config.from_dict(config)` + `Inference(config)` |
| `BayesNet().load(path)`, `load_config(path)` | `Config.load(path)` |
| `bayes_net.add_context(...)` etc. | `config.add_context(...)` etc. |
| `bayes_net.validate_config()` | `config.validate()` |
| `bayes_net.infer(evidence)` | `Inference(config).infer(evidence)` |
| `bayes_net.save(path)` | `config.save(path)` |
"""

# System imports
from __future__ import annotations

import logging
import warnings
from collections import defaultdict

# 3rd party imports

# local imports
from .infer import Inference, normalize
from .model import INFLUENCE_TO_PROBABILITY, Config, PrettySafeLoader  # noqa: F401 - old API

# end file header
__author__ = 'Adrian Lubitz'


def _deprecated(old: str, new: str) -> None:
    """Emit a DeprecationWarning for the caller of the deprecated API.

    Args:
        old: The deprecated name.
        new: What to use instead.
    """
    warnings.warn(f'{old} is deprecated and will be removed in 6.0.0, use {new} instead.',
                  DeprecationWarning, stacklevel=3)


class BayesNet:
    """Deprecated facade over `cobair.model.Config` and `cobair.infer.Inference`.

    `config` is the source of truth like in 4.x: every method reads it, applies the change through
    `Config` and replaces it with the result.
    """

    def __init__(self, config: dict = None, bn_verbosity: int = 0, validate: bool = True) -> None:
        """Initializes the BayesNet with the given config.

        Args:
            config: A dict with a config following the config format.
            bn_verbosity: sets the verbose flag for bnlearn.
            validate: Flag if the given config should be validated or not.
                This is necessary to load invalid configs
        """
        _deprecated('cobair.bayes_net.BayesNet', 'cobair.model.Config and cobair.infer.Inference')
        self.log = logging.getLogger(self.__class__.__name__)
        self.bn_verbosity = bn_verbosity
        self.discretization_functions = {}
        self.value_to_prob = INFLUENCE_TO_PROBABILITY
        self._set_config(Config.from_dict(config), validate=validate and config is not None)

    # ------------------------------------------------------------------------------------------
    # state

    def _model(self) -> Config:
        """Return the current `config` as `Config`.

        Returns:
            Config: The model.
        """
        return Config.from_dict(self.config)

    def _set_config(self, model: Config, validate: bool = True) -> None:
        """Replace the config and rebuild everything that depends on it, like `__init__` in 4.x.

        Args:
            model: The new config.
            validate: Flag if the config should be validated (with warnings).
        """
        self.config = _config_to_default_dict(model.to_dict())
        self.decision_threshold = model.decision_threshold
        self.contexts = self.evidence = list(model.contexts)
        self.intentions = list(model.intentions)
        self.edges = [(context, intention) for context in self.contexts
                      for intention in self.intentions]
        self.evidence_card = [len(model.contexts[context]) for context in self.contexts]
        self.value_to_card = defaultdict(dict, {
            context: {value: card for card, value in enumerate(instantiations)}
            for context, instantiations in model.contexts.items()})
        self.card_to_value = defaultdict(dict, {
            context: dict(enumerate(instantiations))
            for context, instantiations in model.contexts.items()})
        self.valid = self._validate(model) if validate else False
        self.inference = None
        self.cpts = self.DAG = None
        if self.valid:
            self.valid_config = _config_to_default_dict(model.to_dict())
            self.inference = Inference(model, verbosity=self.bn_verbosity)
            self.inference.discretization_functions = self.discretization_functions
            self.cpts = self.inference.tabular_cpds
            self.DAG = self.inference.dag

    def _apply(self, method: str, *args) -> None:
        """Apply an editing method of `Config` and rebuild.

        Args:
            method: Name of the `Config` method.
            *args: Arguments of the method.
        """
        model = self._model()
        getattr(model, method)(*args)
        self._set_config(model)

    @staticmethod
    def _validate(model: Config) -> bool:
        """Validate with a warning for every problem.

        Args:
            model: The config.

        Returns:
            bool: True if the config is valid.
        """
        problems = model.validate()
        for problem in problems:
            warnings.warn(problem, stacklevel=4)
        return not problems

    def validate_config(self) -> bool:
        """Validate that the current config follows the correct format.

        Returns:
            bool: True if config is valid, False otherwise. A warning is raised for every problem.
        """
        model = self._model()
        self.valid = self._validate(model)
        if self.valid:
            self.valid_config = _config_to_default_dict(model.to_dict())
        return self.valid

    # ------------------------------------------------------------------------------------------
    # editing

    def add_context(self, context: str, instantiations: dict):
        """This will add a new context to the config and updates the bayesNet.

        Args:
            context: a new context for the config
            instantiations: a dict of the instantiations and their apriori probabilities
        """
        self._apply('add_context', context, instantiations)

    def add_intention(self, intention: str):
        """This will add a new intention to the config and updates the bayesNet.

        Args:
            intention: Name of a new intention
        """
        self._apply('add_intention', intention)

    def edit_context(self, context: str, instantiations: dict, new_name: str = None):
        """Edits an existing context - this can also be used to remove instantiations.

        Args:
            context: Name of the context to edit
            instantiations: A Dict of instantiations and their apriori probabilities.
            new_name: A new name for the context
        """
        self._apply('edit_context', context, instantiations, new_name)

    def edit_intention(self, intention: str, new_name: str):
        """Edits an existing intention.

        Args:
            intention: Name of the intention to edit
            new_name: A new name for the intention
        """
        self._apply('edit_intention', intention, new_name)

    def del_context(self, context: str):
        """Removes a context.

        Args:
            context: Name of the context to delete
        """
        self._apply('del_context', context)

    def del_intention(self, intention):
        """Remove an intention.

        Args:
            intention: Name of the intention to delete
        """
        self._apply('del_intention', intention)

    def change_context_apriori_value(self, context: str, instantiation, value: float):
        """Changes the apriori_value for a context instantiation.

        Args:
            context: Name of the context
            instantiation: The instantiation for which the apriori value needs to be changed
            value: the new apriori value
        """
        self._apply('change_context_apriori_value', context, instantiation, value)

    def change_influence_value(self, intention: str, context: str, instantiation, value: int):
        """Update the influence value of a specific intention for a particular context instance.

        Args:
            intention: Name of the intention
            context: name of the context
            instantiation: The instantiation for which the influence value should be changed
            value: the new influence value. Can be one out of [0, 1, 2, 3, 4, 5]
        """
        self._apply('change_influence_value', intention, context, instantiation, value)

    def add_combined_influence(self, intention: str, contexts: tuple,
                               instantiations: tuple, value: int):
        """Adds an influence value for a combination of context instantiations.

        Args:
            intention: Name of the intention
            contexts: tuple containing the names of the contexts
            instantiations: Tuple of context instances to set influence value for.
            value: influence value. Can be one out of [0, 1, 2, 3, 4, 5]
        """
        self._apply('add_combined_influence', intention, contexts, instantiations, value)

    def del_combined_influence(self, intention: str, contexts: tuple, instantiations: tuple):
        """Removes the influence value for a combination of context instantiations.

        Args:
            intention: Name of the intention
            contexts: tuple containing the names of the contexts
            instantiations: tuple of context instantiations
        """
        self._apply('del_combined_influence', intention, contexts, instantiations)

    def change_decision_threshold(self, decision_threshold):
        """Changes the decision threshold in the config.

        Args:
            decision_threshold: The new decision threshold.
        """
        self._apply('change_decision_threshold', decision_threshold)

    # ------------------------------------------------------------------------------------------
    # files

    def save(self, path: str, save_invalid: bool = True):
        """Saves the config of the bayesNet to a yml file.

        Args:
            path: path to the file the config will be saved in
            save_invalid: Flag to decide if invalid configs can be saved
        """
        if not self.valid and not save_invalid:
            warnings.warn("Invalid configuration will not be saved.", stacklevel=2)
        else:
            self._model().save(path)

    def load(self, path: str):
        """Loads a config from file and reinitializes the bayesNet.

        Args:
            path: path to the file the config is saved in
        """
        self._set_config(Config.load(path))

    # ------------------------------------------------------------------------------------------
    # inference

    def bind_discretization_function(self, context, discretization_function):
        """Binds a discretization_function to a specific context.

        Args:
            context: One of the possible contexts from the config
            discretization_function: A discretization function which has to take one parameter
                and return one of the possible discrete context instantiations.

        Raises:
            ValueError: If the context does not exist.
        """
        if context not in self.contexts:
            raise ValueError(
                f'Cannot bind discretization function to {context}. Context does not exist!')
        self.discretization_functions[context] = discretization_function

    def valid_evidence(self, context: str, instantiation) -> tuple[bool, str]:
        """Tests if evidence is a valid instantiation for the context.

        Args:
            context: a context
            instantiation: an instantiation of the context

        Returns:
            tuple[bool, str]: validity and an error/warn message

        Raises:
            ValueError: If the config is invalid.
        """
        if self.inference is None:
            raise ValueError('Invalid configuration')
        return self.inference.check_evidence(context, instantiation)

    def infer(self, evidence, normalized=True, decision_threshold=None) -> tuple:
        """Infers the probabilities for the intentions with given evidence.

        Args:
            evidence: Evidence to infer the probabilities of all intentions.
            normalized: Flag if the returned inference is normalized to sum up to 1.
            decision_threshold: a threshold for picking the most likely intention.

        Returns:
            tuple: the highest ranking intention (or None), the decision threshold and a
                dictionary of intentions and the corresponding probabilities.

        Raises:
            ValueError: If the config is invalid.
        """
        if not self.valid or self.inference is None:
            raise ValueError('Invalid configuration')
        return self.inference.infer(evidence, normalized, decision_threshold)

    def normalize_inference(self, inference: dict) -> dict:
        """Normalizes the inference to a proper probability distribution.

        Args:
            inference: dictionary of intentions and the corresponding probabilities

        Returns:
            dict: dictionary of intentions and the corresponding normalized probabilities.
        """
        return normalize(inference)

    # ------------------------------------------------------------------------------------------
    # internals used by old tests

    def _calculate_probability_values(self, context_influence: dict) -> list:
        """Calculates the probability values with the given context_influence from the config.

        Args:
            context_influence: A dict with the influence values for contexts.

        Returns:
            list: `[negative values, positive values]`
        """
        states = {context: list(instantiations)
                  for context, instantiations in self.config['contexts'].items()}
        # pylint: disable-next=protected-access
        return Config._intention_values(self.evidence, states, context_influence)

    def _create_combined_context(self, context_influence: dict) -> dict:
        """Creates a dict with the combined contexts in card index format from context_influence.

        Args:
            context_influence: A dict with the influence values for contexts.

        Returns:
            dict: `{(context index, ...): {(instantiation, ...): influence}}`
        """
        return {tuple(map(self.evidence.index, context)): values
                for context, values in context_influence.items() if isinstance(context, tuple)}


def _config_to_default_dict(config: dict = None) -> dict:
    """Cast a config into nested defaultdicts.

    Args:
        config: A dict with a config following the config format.

    Returns:
        dict: The config with defaultdicts.
    """
    config = config or {}
    new_config = {'intentions': defaultdict(lambda: defaultdict(lambda: defaultdict(int))),
                  'contexts': defaultdict(lambda: defaultdict(float))}
    for context, instantiations in config.get('contexts', {}).items():
        for instantiation, value in instantiations.items():
            new_config['contexts'][context][instantiation] = value
    for intention, influences in config.get('intentions', {}).items():
        new_config['intentions'][intention] = defaultdict(lambda: defaultdict(int))
        for context, values in influences.items():
            for instantiation, value in values.items():
                new_config['intentions'][intention][context][instantiation] = value
    new_config['decision_threshold'] = config.get('decision_threshold', 0.0)
    return new_config


def config_to_default_dict(config: dict = None) -> dict:
    """This casts a config given as dict into a defaultdict.

    Args:
        config: A dict with a config following the config format.

    Returns:
        dict: a defaultdict containing the config
    """
    _deprecated('config_to_default_dict', 'cobair.model.Config.from_dict')
    return _config_to_default_dict(config)


def load_config(path) -> dict:
    """Helper function to load a config.

    Args:
        path: path to the file the config is saved in

    Returns:
        dict: a defaultdict containing the config
    """
    _deprecated('load_config', 'cobair.model.Config.load')
    return _config_to_default_dict(Config.load(path).to_dict())


def default_to_regular(d):
    """This casts a defaultdict to a regular dict which is needed for saving as yml file.

    Args:
        d: the dict which should be casted

    Returns:
        dict: a regular dict casted from the defaultdict
    """
    _deprecated('default_to_regular', 'cobair.model.Config.to_dict')
    return _default_to_regular(d)


def _default_to_regular(d):
    """Cast nested defaultdicts to regular dicts, dropping empty plain dicts like 4.x.

    Args:
        d: the dict which should be casted

    Returns:
        dict: a regular dict
    """
    if isinstance(d, dict):
        d = {key: _default_to_regular(value) for key, value in d.items()
             if not isinstance(value, dict) or value or isinstance(value, defaultdict)}
    return d


__all__ = ['BayesNet', 'PrettySafeLoader', 'config_to_default_dict', 'load_config',
           'default_to_regular']
