"""
This module contains some default decorator functions to dicretize 
"""


def discretized_1d_range(ranges, values, deafult):
    """
    Decorator for 1d range discretization. It takes a set of ranges to check against the the corresponding values to return for those ranges.
    If a value is in multiple ranges the first suitable will be used.

    ranges is a list of functions/lambda-statements taking one value as input and returning true or false
    values is a list of the corresponding values
    default is the default value which will be returned if no range returned true
    """
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            result = f(*args, **kwargs)
            # TODO: one-dimensionality
            # TODO: check if in ranges, else return default
        return wrapped_f
    return wrap


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
