"""Inference of intentions from context with the two-layer Bayesian net.

This is a thin adapter: the conditional probability tables are computed by `cobair.model`,
this module hands them to pgmpy / bnlearn. It needs the `[infer]` extra
(`pip install "cobair[infer]"`).

Example:
    ```python
    from cobair.model import Config
    from cobair.infer import Inference

    inference = Inference(Config.load('small_example.yml'))
    intention, decision_threshold, probabilities = inference.infer({'speech commands': 'pickup'})
    ```
"""

# System imports
from __future__ import annotations

import itertools
import warnings
from collections.abc import Callable, Hashable
from typing import NamedTuple

# 3rd party imports
import bnlearn as bn
from pgmpy.factors.discrete import TabularCPD

# local imports
from .model import Config

# end file header
__author__ = 'Adrian Lubitz'


class InferenceResult(NamedTuple):
    """The result of an inference, unpacks like the tuple `BayesNet.infer` returned.

    Attributes:
        intention: The most likely intention or None if its probability doesn't exceed
            the decision threshold.
        decision_threshold: The decision threshold that was used.
        probabilities: `{intention: probability}`
    """

    intention: Hashable | None
    decision_threshold: float
    probabilities: dict


class Inference:
    """Infers the probabilities of the intentions of a valid config.

    The inference works on a copy of the config: create a new `Inference` after editing it.
    """

    def __init__(self, config: Config, verbosity: int = 0) -> None:
        """Build the Bayesian net for a config, which must be valid (else `ValueError`).

        Args:
            config: A valid config.
            verbosity: The verbose flag for bnlearn. See [bnlearn API](
                https://erdogant.github.io/bnlearn/pages/html/bnlearn.bnlearn.html?highlight=verbose
                #bnlearn.bnlearn.make_DAG) for more information.
        """
        self.config = config.copy()
        self.verbosity = verbosity
        self.cpts = self.config.cpts()
        self.discretization_functions = {}
        # bnlearn uses the index of an instantiation (card) instead of the instantiation
        self.value_to_card = {context: {value: card for card, value in enumerate(states)}
                              for context, states in self.cpts.states.items()}
        self.tabular_cpds = self._create_tabular_cpds()
        edges = list(itertools.product(self.cpts.contexts, self.cpts.intentions))
        self.dag = bn.make_DAG(edges, CPD=self.tabular_cpds, verbose=verbosity)

    def _create_tabular_cpds(self) -> list:
        """Wrap the CPTs in pgmpy TabularCPDs.

        Returns:
            list: One TabularCPD per context and intention.
        """
        cpds = [TabularCPD(variable=context, variable_card=len(priors),
                           values=[[prior] for prior in priors])
                for context, priors in self.cpts.context_priors.items()]
        cpds += [TabularCPD(variable=intention,
                            variable_card=2,  # intentions are always binary
                            values=values,
                            evidence=self.cpts.contexts,
                            evidence_card=self.cpts.cards)
                 for intention, values in self.cpts.intention_values.items()]
        return cpds

    def bind_discretization_function(self, context: Hashable,
                                     discretization_function: Callable) -> None:
        """Bind a discretization function to a context.

        Args:
            context: One of the contexts of the config.
            discretization_function: A function which takes one parameter and returns one of the
                instantiations of the context.

        Raises:
            ValueError: If the context does not exist.
        """
        if context not in self.config.contexts:
            raise ValueError(
                f'Cannot bind discretization function to {context}. Context does not exist!')
        self.discretization_functions[context] = discretization_function

    def check_evidence(self, context: Hashable, instantiation) -> tuple[bool, str]:
        """Check if an instantiation is valid evidence for a context.

        Args:
            context: A context.
            instantiation: An instantiation of the context.

        Returns:
            tuple[bool, str]: Validity and an error or warning message (empty if fine).
        """
        if context not in self.config.contexts:
            return True, f'Context "{context}" not set in config - will be ignored'
        if not isinstance(instantiation, Hashable):
            return False, ('Context instatiations must be hashable! '
                           f'Instantiation "{instantiation}" for context "{context}" '
                           'is not hashable!')
        if instantiation is None:
            return True, (f'No instantiation given for context "{context}" - '
                          'A prori values will be used.')
        if instantiation not in self.config.contexts[context]:
            return True, (f'"{instantiation}" is not a valid instantiation for "{context}". '
                          f'Using None instead Valid options are '
                          f'{list(self.config.contexts[context])}')
        return True, ''

    def _is_instantiation(self, context: Hashable, value) -> bool:
        """Check if value is one of the instantiations of a context.

        Args:
            context: A context of the config.
            value: Any value.

        Returns:
            bool: True if value is an instantiation of the context.
        """
        return isinstance(value, Hashable) and value in self.config.contexts[context]

    def _card_evidence(self, evidence: dict) -> dict:
        """Translate evidence into bnlearn's card form.

        Discretization functions are applied to values that are not an instantiation.

        Args:
            evidence: `{context: instantiation}`

        Returns:
            dict: `{context: card}` of all usable evidence.

        Raises:
            ValueError: If evidence is invalid.
        """
        card_evidence = {}
        errors = []
        for context, instantiation in evidence.items():
            if context in self.discretization_functions and instantiation is not None and \
                    not self._is_instantiation(context, instantiation):
                instantiation = self.discretization_functions[context](instantiation)
            valid, message = self.check_evidence(context, instantiation)
            if not valid:
                errors.append(message)
            elif message:
                warnings.warn(message, stacklevel=3)
            else:
                card_evidence[context] = self.value_to_card[context][instantiation]
        if errors:
            raise ValueError(f'{errors}')
        return card_evidence

    def infer(self, evidence: dict, normalized: bool = True,
              decision_threshold: float = None) -> InferenceResult:
        """Infer the probabilities of the intentions given evidence.

        Args:
            evidence: `{context: instantiation}`, e.g. `{'speech commands': 'pickup'}`.
                Contexts which are not in the config are ignored (with a warning),
                contexts which are not given use their apriori probabilities.
            normalized: Normalize the probabilities to sum up to 1.
            decision_threshold: A threshold for picking the most likely intention, between 0
                and 1. Defaults to the decision threshold of the config.

        Returns:
            InferenceResult: The most likely intention (None if the decision threshold is not
                exceeded), the decision threshold and the probabilities of all intentions.
        """
        if decision_threshold is None:
            decision_threshold = self.config.decision_threshold
        card_evidence = self._card_evidence(evidence)
        # only the probability of the True state of the binary intentions is kept
        probabilities = {
            intention: bn.inference.fit(self.dag, variables=[intention], evidence=card_evidence,
                                        verbose=self.verbosity).values[1]
            for intention in self.cpts.intentions}
        if normalized:
            probabilities = normalize(probabilities)
        best = max(probabilities, key=probabilities.get)
        if probabilities[best] <= decision_threshold:
            best = None
        return InferenceResult(best, decision_threshold, probabilities)


def normalize(probabilities: dict) -> dict:
    """Normalize the probabilities of the intentions to a probability distribution.

    Each intention is inferred independently as True or False, so the raw probabilities don't sum
    up to 1 and can't be compared as a distribution over intentions.

    Args:
        probabilities: `{intention: probability}`

    Returns:
        dict: `{intention: normalized probability}`
    """
    total = sum(probabilities.values())
    return {intention: probability / total for intention, probability in probabilities.items()}
