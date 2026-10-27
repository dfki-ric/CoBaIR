"""
This module contains some default functions to discretize incoming evidence

!!! note
    If you want to bindb a discretizer with different default values using 
    `bayes_net.bind_discretization_function` you have to wrap it in a lambda
    function like this: 

    ```
    net.bind_discretization_function('some context', lambda x: binary_decision(x, decision_boundary=0.7))
    ```
"""


def binary_decision(prob_value: float, decision_boundary: float = 0.5, flip: bool = False):
    """
    This function discretizes a probability value into the discrete values True and False.

    Args:
        prob_value: A probability value between 0 and 1
        decision_boundary: Values >= this decision boundary will be discretized as True
        flip: A flag which decides if the discrete result is flipped
    Returns:
        bool:
            A boolean discretization of the given probaility value
    Raises:
        ValueError: A ValueError is raised if the probability value is not in the range [0.0, 1.0]
    """
    if prob_value > 1.0 or prob_value < 0.0:
        raise ValueError(
            f'Probability values have to be in the range of [0.0, 1.0]. Given value is {prob_value}')
    if prob_value >= decision_boundary:
        return True != flip
    else:
        return False != flip
