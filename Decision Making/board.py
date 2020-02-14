import copy

from action import Action


class Board:

    # index 0-23: points 1-24 for player 0 and points 24-1 for player 1
    INITIAL_POINTS = [
        [0,2],
        [0,0],
        [0,0],
        [0,0],
        [0,0],
        [5,0],
        [0,0],
        [3,0],
        [0,0],
        [0,0],
        [0,0],
        [0,5],
        [5,0],
        [0,0],
        [0,0],
        [0,0],
        [0,3],
        [0,0],
        [0,5],
        [0,0],
        [0,0],
        [0,0],
        [0,0],
        [2,0],
    ]

    def __init__(self):
        self.points = [
                        [0,2],
                        [0,0],
                        [0,0],
                        [0,0],
                        [0,0],
                        [5,0],
                        [0,0],
                        [3,0],
                        [0,0],
                        [0,0],
                        [0,0],
                        [0,5],
                        [5,0],
                        [0,0],
                        [0,0],
                        [0,0],
                        [0,3],
                        [0,0],
                        [0,5],
                        [0,0],
                        [0,0],
                        [0,0],
                        [0,0],
                        [2,0],
                    ]
        self.bar = [0,0]
        self.off = [0,0]
        self.homed = [5,5]

    def clone(self):
        return copy.deepcopy(self)