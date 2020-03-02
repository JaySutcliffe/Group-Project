from collections import namedtuple

WHITE = 0
BLACK = 1

"""
An action is made up of 1 or 2 Steps depending on whether a piece is knocked off or not.
A Step is a movement of a checker from one point (start) to another (end). The points are from the perspective of BLACK.
"""
Step = namedtuple('Step', ['player', 'start', 'end'])


class Action:
    """
    A move is made up of multiple Actions corresponding to each dice roll.
    """

    BAR = "BAR"
    OFF_BOARD = "OFF"

    def __init__(self, player, start, end, roll, bars=False):
        """
        Constructs an Action object.
        
        :param player: WHITE (0) or BLACK (1) Player whose turn it is.
        :param start: Integer or BAR ("BAR"). From which point (or bar) the checker is being moved (from player's 
            perspective).
        :param end: Integer or OFF_BOARD ("OFF"). To which point (or off board) the checker is being moved (from 
            player's perspective).
        :param roll: Integer. The dice roll corresponding to this action.
        :param bars: Boolean. Whether or not the action involves the opponent's player being knocked off.
        """

        self.player = player
        self.start = start
        self.end = end
        self.roll = roll
        self.bars = bars

    def get_raw_steps(self):
        """
        
        :return: Convert action to list of Steps.
        """
        steps = []
        s = self.start if self.start == Action.BAR or self.player == WHITE else 23 - self.start
        e = self.end if self.end == Action.OFF_BOARD or self.player == WHITE else 23 - self.end
        if self.bars:
            steps.append(Step(player=int(not self.player), start=e, end=Action.BAR))
        steps.append(Step(player=int(self.player), start=s, end=e))
        return steps

    def __str__(self):
        return str(self.get_raw_steps())
        #return "Action({}, {}, {}, {}, {})".format(self.player, self.start, self.end, self.roll, self.bars)
    def __repr__(self):
        return str(self.get_raw_steps())
        #return "Action({}, {}, {}, {}, {})".format(self.player, self.start, self.end, self.roll, self.bars)
