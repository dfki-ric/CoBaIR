"""The config model of CoBaIR: contexts, intentions, influences and the decision threshold.

This module is pure Python (it only needs pyyaml), so it can be used without the inference
dependencies, e.g. in the GUIs. The conditional probability tables of the two-layer Bayesian net
are computed here as well, `cobair.infer` only hands them to pgmpy.

Example:
    ```python
    from cobair.model import Config

    config = Config.load('small_example.yml')
    config.add_context('weather', {'sunny': 0.7, 'rainy': 0.3})
    config.change_influence_value('pick up tool', 'weather', 'rainy', 4)
    print(config.validate())  # [] if the config is valid
    config.save('my_config.yml')
    ```
"""

# System imports
from __future__ import annotations

import itertools
import math
from copy import deepcopy
from dataclasses import dataclass
from numbers import Real
from pathlib import Path
from typing import Hashable

# 3rd party imports
import yaml

# local imports
from . import __version__

# end file header
__author__ = 'Adrian Lubitz'

#: Version of the YAML config format written by this module.
FORMAT_VERSION = 1

#: Translation of the influence values to the probability of an intention given the context.
#: [very high, high, medium, low, very low, no] => [5, 4, 3, 2, 1, 0]
INFLUENCE_TO_PROBABILITY = {5: 0.95, 4: 0.75, 3: 0.5, 2: 0.25, 1: 0.05, 0: 0.0}

HEADER = """\
# CoBaIR configuration, see https://dfki-ric.github.io/CoBaIR/
# This file is generated. Edit it with a CoBaIR GUI unless you know exactly what you are doing:
#   cobair-web          (pip install "cobair[web]")
#   cobair-qt           (pip install "cobair[qt]")
"""


class PrettySafeLoader(yaml.SafeLoader):  # pylint: disable=too-many-ancestors
    """A YAML loader that constructs Python tuples from YAML sequences."""

    def construct_python_tuple(self, node):
        """Construct a Python tuple from a YAML sequence node.

        Args:
            node (Any): The YAML sequence node to construct a tuple from.

        Returns:
            tuple: The constructed tuple.
        """
        return tuple(self.construct_sequence(node))


PrettySafeLoader.add_constructor(
    'tag:yaml.org,2002:python/tuple',
    PrettySafeLoader.construct_python_tuple)


class _Dumper(yaml.SafeDumper):  # pylint: disable=too-many-ancestors
    """A YAML dumper that writes tuples (used as keys for combined influences)."""

    def represent_tuple(self, data):
        """Represent a tuple as a `!!python/tuple` sequence.

        Args:
            data: The tuple.

        Returns:
            The YAML node.
        """
        return self.represent_sequence('tag:yaml.org,2002:python/tuple', data)


_Dumper.add_representer(tuple, _Dumper.represent_tuple)


def _is_number(value) -> bool:
    """Check if value is a real number (bool is not a number here).

    Args:
        value: The value to check.

    Returns:
        True if value is an int or float but not a bool.
    """
    return isinstance(value, Real) and not isinstance(value, bool)


@dataclass
class CPTs:
    """The conditional probability tables of the two-layer Bayesian net.

    The order of the states is the order of the instantiations in the config.
    The columns of the intention tables iterate over all combinations of context instantiations
    in the order of `contexts`, the last context changes fastest (the order pgmpy expects).

    Attributes:
        contexts: All contexts, the parents of every intention.
        states: The instantiations of every context.
        context_priors: The apriori probability of every instantiation of every context.
        intentions: All intentions.
        intention_values: For every intention `[negative values, positive values]`.
    """

    contexts: list
    states: dict
    context_priors: dict
    intentions: list
    intention_values: dict

    @property
    def cards(self) -> list:
        """The number of instantiations of every context in the order of `contexts`.

        Returns:
            list: The cardinalities.
        """
        return [len(self.states[context]) for context in self.contexts]


class Config:
    """A mutable CoBaIR config.

    Attributes:
        contexts: `{context: {instantiation: apriori probability}}`
        intentions: `{intention: {context: {instantiation: influence}}}`. Combined influences use
            a tuple of contexts as context key and a tuple of instantiations as instantiation key.
        decision_threshold: The probability an intention must exceed to be picked.
    """

    def __init__(self, contexts: dict = None, intentions: dict = None,
                 decision_threshold: float = 0.0) -> None:
        """Create a config, the given dicts are copied.

        Args:
            contexts: `{context: {instantiation: apriori probability}}`
            intentions: `{intention: {context: {instantiation: influence}}}`
            decision_threshold: The probability an intention must exceed to be picked.
        """
        self.contexts = _to_plain(contexts or {})
        self.intentions = _to_plain(intentions or {})
        self.decision_threshold = decision_threshold

    # ------------------------------------------------------------------------------------------
    # conversion and files

    @classmethod
    def from_dict(cls, config: dict) -> Config:
        """Create a config from a dict in the config file format; unknown keys are ignored.

        Args:
            config: A dict with the keys `contexts`, `intentions` and `decision_threshold`.

        Returns:
            Config: The new config.
        """
        config = config or {}
        return cls(config.get('contexts'), config.get('intentions'),
                   config.get('decision_threshold', 0.0))

    def to_dict(self) -> dict:
        """Return the config as plain dicts in the config file format (without header).

        Returns:
            dict: A deep copy of the config.
        """
        return {'contexts': deepcopy(self.contexts),
                'intentions': deepcopy(self.intentions),
                'decision_threshold': self.decision_threshold}

    def copy(self) -> Config:
        """Return a deep copy.

        Returns:
            Config: The copy.
        """
        return Config.from_dict(self.to_dict())

    @classmethod
    def loads(cls, text: str) -> Config:
        """Create a config from YAML text.

        Args:
            text: The content of a config file.

        Returns:
            Config: The loaded config.

        Raises:
            ValueError: If the text is not a mapping or was written with a newer format version.
        """
        data = yaml.load(text, Loader=PrettySafeLoader)  # noqa: S506 - safe loader + tuples
        if data is None:
            data = {}
        if not isinstance(data, dict):
            raise ValueError('A config must be a YAML mapping')
        format_version = data.get('format_version', FORMAT_VERSION)
        if not isinstance(format_version, int) or format_version > FORMAT_VERSION:
            raise ValueError(
                f'The config has format version {format_version}, but cobair {__version__} '
                f'only supports up to version {FORMAT_VERSION}. Please update cobair.')
        return cls.from_dict(data)

    @classmethod
    def load(cls, path) -> Config:
        """Load a config from a YAML file.

        Args:
            path: Path to the config file.

        Returns:
            Config: The loaded config.
        """
        return cls.loads(Path(path).read_text(encoding='utf-8'))

    def dumps(self) -> str:
        """Return the config as YAML text with header.

        Returns:
            str: The content of a config file.
        """
        data = {'format_version': FORMAT_VERSION, 'created_with': f'cobair {__version__}'}
        data.update(self.to_dict())
        return HEADER + yaml.dump(data, Dumper=_Dumper, sort_keys=False, allow_unicode=True)

    def save(self, path) -> None:
        """Save the config to a YAML file.

        Args:
            path: Path to the config file.
        """
        Path(path).write_text(self.dumps(), encoding='utf-8')

    def __eq__(self, other) -> bool:
        """Configs are equal if contexts, intentions and decision threshold are equal.

        Args:
            other: The object to compare with.

        Returns:
            bool: True if equal.
        """
        if not isinstance(other, Config):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        """Return a short representation.

        Returns:
            str: The representation.
        """
        return (f'Config(contexts={list(self.contexts)}, intentions={list(self.intentions)}, '
                f'decision_threshold={self.decision_threshold})')

    # ------------------------------------------------------------------------------------------
    # validation

    def validate(self) -> list:
        """Check that the config is complete and consistent.

        Returns:
            list: Messages describing all problems, empty if the config is valid.
        """
        problems = []
        if not self.contexts:
            problems.append('No contexts defined')
        if not self.intentions:
            problems.append('No intentions defined')
        if not _is_number(self.decision_threshold) or not 0 <= self.decision_threshold < 1:
            problems.append('Decision threshold must be a number between 0 and 1')

        for context, instantiations in self.contexts.items():
            for instantiation, value in instantiations.items():
                if not _is_number(value):
                    problems.append(
                        f'Apriori probability of context "{context}.{instantiation}" '
                        'is not a number')
            values = [value for value in instantiations.values() if _is_number(value)]
            if len(values) == len(instantiations) and \
                    not math.isclose(sum(values), 1.0, abs_tol=1e-9):
                problems.append(
                    'The sum of probabilities for context instantiations must be 1 - '
                    f'For "{context}" it is {sum(values)}!')

        for intention, influences in self.intentions.items():
            for context, values in influences.items():
                problems.extend(self._validate_influences(intention, context, values))
        return problems

    def _validate_influences(self, intention, context, values: dict) -> list:
        """Check the influence values of one intention for one (combined) context.

        Args:
            intention: The intention.
            context: A context or a tuple of contexts.
            values: `{instantiation: influence}`

        Returns:
            list: Messages describing all problems.
        """
        problems = []
        contexts = context if isinstance(context, tuple) else (context,)
        unknown = [name for name in contexts if name not in self.contexts]
        if unknown:
            return [f'Context influence {context} of {intention} cannot be found in the defined '
                    f'contexts! Unknown: {unknown}']
        for instantiation, influence in values.items():
            if isinstance(context, tuple):
                if not isinstance(instantiation, tuple) or len(instantiation) != len(context) \
                        or any(inst not in self.contexts[name]
                               for name, inst in zip(context, instantiation)):
                    problems.append(f'{instantiation} is not a valid combination of '
                                    f'instantiations for {context} in {intention}')
            elif instantiation not in self.contexts[context]:
                problems.append(
                    'An influence needs to be defined for all instantiations! '
                    f'{intention}.{context}.{instantiation} does not fit the defined '
                    f'instantiations for {context}')
            if not (isinstance(influence, int) and not isinstance(influence, bool)
                    and 0 <= influence <= 5):
                problems.append(f'Influence Value for {intention}.{context}.{instantiation} '
                                f'must be an integer between 0 and 5! Is {influence}')
        return problems

    @property
    def valid(self) -> bool:
        """True if `validate()` finds no problems.

        Returns:
            bool: Validity of the config.
        """
        return not self.validate()

    # ------------------------------------------------------------------------------------------
    # editing

    def add_context(self, context: Hashable, instantiations: dict) -> None:
        """Add a new context; its influence on all intentions is set to 0.

        Args:
            context: Name of the new context.
            instantiations: `{instantiation: apriori probability}`, e.g. `{True: 0.6, False: 0.4}`

        Raises:
            ValueError: If the context already exists.
        """
        if context in self.contexts:
            raise ValueError(
                'Cannot add existing context - use edit_context to edit an existing context')
        self.contexts[context] = dict(instantiations)
        self._sync_influences()

    def edit_context(self, context: Hashable, instantiations: dict,
                     new_name: Hashable = None) -> None:
        """Change the instantiations of a context and optionally rename it.

        Influences of removed instantiations are removed, new instantiations get the influence 0.
        Combined influences follow a rename and are removed if they use a removed instantiation.

        !!! note
            Changing the name of an instantiation will always set the influence value of this
                instantiation to zero for all intentions!

        Args:
            context: Name of the context to edit.
            instantiations: `{instantiation: apriori probability}`, e.g. `{True: 0.6, False: 0.4}`
            new_name: A new name for the context.

        Raises:
            ValueError: If the context does not exist or `new_name` is another existing context.
        """
        if context not in self.contexts:
            raise ValueError(
                'Cannot edit non existing context - use add_context to add a new context')
        if new_name is not None and new_name != context:
            if new_name in self.contexts:
                raise ValueError(f'Cannot rename "{context}" to "{new_name}" - it exists already')
            self.contexts = _rename_key(self.contexts, context, new_name)
            for intention, influences in self.intentions.items():
                renamed = {}
                for key, values in influences.items():
                    if key == context:
                        renamed[new_name] = values
                    elif isinstance(key, tuple) and context in key:
                        renamed[tuple(new_name if name == context else name for name in key)] = \
                            values
                    else:
                        renamed[key] = values
                self.intentions[intention] = renamed
            context = new_name
        self.contexts[context] = dict(instantiations)
        self._sync_influences()

    def del_context(self, context: Hashable) -> None:
        """Remove a context including all its (combined) influences.

        Args:
            context: Name of the context to delete.

        Raises:
            ValueError: If the context does not exist.
        """
        if context not in self.contexts:
            raise ValueError(
                'Cannot delete non-existing context - use add_context to add a new context')
        del self.contexts[context]
        self._sync_influences()

    def add_intention(self, intention: Hashable) -> None:
        """Add a new intention; the influence of all contexts is set to 0.

        Args:
            intention: Name of the new intention.

        Raises:
            ValueError: If the intention already exists.
        """
        if intention in self.intentions:
            raise ValueError(
                'Cannot add existing intention - use edit_intention to edit an existing intention')
        self.intentions[intention] = {}
        self._sync_influences()

    def edit_intention(self, intention: Hashable, new_name: Hashable) -> None:
        """Rename an intention.

        Args:
            intention: Name of the intention to edit.
            new_name: A new name for the intention.

        Raises:
            ValueError: If the intention does not exist or `new_name` exists already.
        """
        if intention not in self.intentions:
            raise ValueError(
                'Cannot edit non existing intention - use add_intention to add a new intention')
        if new_name in self.intentions:
            raise ValueError(f'{new_name} exists - cannot be given as the new name for {intention}')
        self.intentions = _rename_key(self.intentions, intention, new_name)

    def del_intention(self, intention: Hashable) -> None:
        """Remove an intention.

        Args:
            intention: Name of the intention to delete.

        Raises:
            ValueError: If the intention does not exist.
        """
        if intention not in self.intentions:
            raise ValueError(
                'Cannot delete non existing intention - use add_intention to add a new intention')
        del self.intentions[intention]

    def change_context_apriori_value(self, context: Hashable, instantiation: Hashable,
                                     value: float) -> None:
        """Change the apriori probability of a context instantiation.

        Args:
            context: Name of the context.
            instantiation: The instantiation.
            value: The new apriori probability.

        Raises:
            ValueError: If the context or instantiation does not exist.
        """
        if instantiation not in self.contexts.get(context, {}):
            raise ValueError(
                'change_context_apriori_value can only change values that exist already')
        self.contexts[context][instantiation] = value

    def change_influence_value(self, intention: Hashable, context: Hashable,
                               instantiation: Hashable, value: int) -> None:
        """Change the influence of a context instantiation on an intention.

        Args:
            intention: Name of the intention.
            context: Name of the context (or tuple of contexts for a combined influence).
            instantiation: The instantiation (or tuple of instantiations).
            value: The new influence value, one out of [0, 1, 2, 3, 4, 5].

        Raises:
            ValueError: If the influence does not exist.
        """
        if instantiation not in self.intentions.get(intention, {}).get(context, {}):
            raise ValueError('change_influence_value can only change values that exist already')
        self.intentions[intention][context][instantiation] = value

    def add_combined_influence(self, intention: Hashable, contexts: tuple,
                               instantiations: tuple, value: int) -> None:
        """Set the influence of a combination of context instantiations on an intention.

        If all instantiations of the combination are present, the combined influence replaces
        the single influences of these contexts.

        Args:
            intention: Name of the intention.
            contexts: The names of the contexts.
            instantiations: One instantiation for each of the contexts.
            value: The influence value, one out of [0, 1, 2, 3, 4, 5].

        Raises:
            ValueError: If the contexts are empty, the intention does not exist or an
                instantiation does not exist.
        """
        if not contexts:
            raise ValueError('Contexts list cannot be empty.')
        if intention not in self.intentions:
            raise ValueError(f'"{intention}" does not exist in the list of intentions')
        contexts, instantiations = tuple(contexts), tuple(instantiations)
        if len(contexts) != len(instantiations) or any(
                instantiation not in self.contexts.get(context, {})
                for context, instantiation in zip(contexts, instantiations)):
            raise ValueError(
                'add_combined_influence can only combine context instantiations that already exist')
        self.intentions[intention].setdefault(contexts, {})[instantiations] = value

    def del_combined_influence(self, intention: Hashable, contexts: tuple,
                               instantiations: tuple) -> None:
        """Remove the combined influence of a combination of context instantiations.

        Args:
            intention: Name of the intention.
            contexts: The names of the contexts.
            instantiations: One instantiation for each of the contexts.

        Raises:
            ValueError: If the combined influence does not exist.
        """
        contexts, instantiations = tuple(contexts), tuple(instantiations)
        combinations = self.intentions.get(intention, {}).get(contexts, {})
        if instantiations not in combinations:
            raise ValueError('Combined context instantiations must exist to be removed.')
        del combinations[instantiations]
        if not combinations:
            del self.intentions[intention][contexts]

    def change_decision_threshold(self, decision_threshold: float) -> None:
        """Change the decision threshold.

        Args:
            decision_threshold: The new decision threshold.
        """
        self.decision_threshold = decision_threshold

    def combined_influences(self, intention: Hashable) -> dict:
        """Return the combined influences of an intention.

        Args:
            intention: Name of the intention.

        Returns:
            dict: `{(context, ...): {(instantiation, ...): influence}}`
        """
        return {contexts: values for contexts, values in self.intentions[intention].items()
                if isinstance(contexts, tuple)}

    def _sync_influences(self) -> None:
        """Make the influences of all intentions match the contexts and their instantiations."""
        for intention, influences in self.intentions.items():
            synced = {}
            for context, instantiations in self.contexts.items():
                old = influences.get(context, {})
                synced[context] = {instantiation: old.get(instantiation, 0)
                                   for instantiation in instantiations}
            for contexts, combinations in influences.items():
                if not isinstance(contexts, tuple) or \
                        any(context not in self.contexts for context in contexts):
                    continue
                kept = {instantiations: value for instantiations, value in combinations.items()
                        if all(instantiation in self.contexts[context]
                               for context, instantiation in zip(contexts, instantiations))}
                if kept:
                    synced[contexts] = kept
            self.intentions[intention] = synced

    # ------------------------------------------------------------------------------------------
    # conditional probability tables

    def cpts(self) -> CPTs:
        """Compute the conditional probability tables of the two-layer Bayesian net.

        The probability of an intention for a combination of context instantiations is the
        average of the probabilities of the influences (see `INFLUENCE_TO_PROBABILITY`).
        If a combined influence matches the combination, its value replaces the single influences
        of the combined contexts; if several match, the first one wins.

        Returns:
            CPTs: The conditional probability tables.

        Raises:
            ValueError: If the config is not valid.
        """
        problems = self.validate()
        if problems:
            raise ValueError(f'Invalid configuration: {problems}')
        contexts = list(self.contexts)
        states = {context: list(instantiations) for context, instantiations in
                  self.contexts.items()}
        priors = {context: list(instantiations.values()) for context, instantiations in
                  self.contexts.items()}
        values = {intention: self._intention_values(contexts, states, influences)
                  for intention, influences in self.intentions.items()}
        return CPTs(contexts, states, priors, list(self.intentions), values)

    @staticmethod
    def _intention_values(contexts: list, states: dict, influences: dict) -> list:
        """Compute the CPT of one intention.

        Args:
            contexts: All contexts in CPT order.
            states: The instantiations of every context.
            influences: `{context: {instantiation: influence}}` of the intention.

        Returns:
            list: `[negative values, positive values]`
        """
        combined = [(names, combination, value)
                    for names, combinations in influences.items() if isinstance(names, tuple)
                    for combination, value in combinations.items()]
        positive = []
        for case in itertools.product(*(states[context] for context in contexts)):
            active = dict(zip(contexts, case))
            # missing influences count as 0
            case_influences = {context: influences.get(context, {}).get(active[context], 0)
                               for context in contexts}
            for names, combination, value in combined:
                if all(active[name] == instantiation
                       for name, instantiation in zip(names, combination)):
                    case_influences.update(dict.fromkeys(names, value))
                    break
            probabilities = [INFLUENCE_TO_PROBABILITY.get(influence, 0)
                             for influence in case_influences.values()]
            positive.append(sum(probabilities) / len(probabilities) if probabilities else 0)
        return [[1 - value for value in positive], positive]


def _to_plain(data):
    """Deep copy nested (default)dicts into plain dicts.

    Args:
        data: A value, possibly a nested dict.

    Returns:
        The copy.
    """
    if isinstance(data, dict):
        return {key: _to_plain(value) for key, value in data.items()}
    return deepcopy(data)


def _rename_key(data: dict, old: Hashable, new: Hashable) -> dict:
    """Return a copy of data with `old` renamed to `new`, keeping the order.

    Args:
        data: The dict.
        old: The key to rename.
        new: The new key.

    Returns:
        dict: The dict with the renamed key.
    """
    return {new if key == old else key: value for key, value in data.items()}
