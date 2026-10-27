'''
This module helps to increment in a CPT with random number of cards per evidence.
'''

# System imports

# 3rd party imports

# local imports

# end file header
__author__ = 'Adrian Lubitz'


class Counter():
    """A counter for different bases on different positions"""

    def __init__(self, evidence_cards: list) -> None:
        '''
        Takes a list of ints (int must be >=2) and creates the counter

        Args:
            evidence_cards: list of ints as mapping of base to position
        '''
        self.evidence_cards = evidence_cards
        self.current_evidence = [0] * len(self.evidence_cards)
        self.first_call = True

    def __iter__(self):
        """Returns self as a iterator"""
        return self

    def __next__(self, start=-1):
        '''
        increment by one.
        '''
        # Corner Cases: First Call
        if self.first_call:
            self.first_call = False
            return self.current_evidence
        # Corner Cases: Last Call
        if start < -1*len(self.evidence_cards):
            raise StopIteration()
        # Std Case: All other calls
        self.current_evidence[start] += 1
        while(self.current_evidence[start] == self.evidence_cards[start]):
            self.current_evidence[start] = 0
            self.__next__(start-1)
        return self.current_evidence


if __name__ == '__main__':
    # Testing
    for count in Counter([4, 2, 3, 2]):
        print(count)
