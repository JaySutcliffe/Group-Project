from collections import namedtuple

Step = namedtuple('Step', ['player', 'start', 'end'])


class Action:
    BAR = "BAR"
    OFF_BOARD = "OFF"

    def __init__(self, player, start, end, roll, bars=False):
        self.player = player
        self.start = start
        self.end = end
        self.roll = roll
        self.bars = bars

    def get_raw_steps(self):
        steps = []
        s = self.start if self.start == Action.BAR or self.player == 0 else 23-self.start
        e = self.end if self.end == Action.OFF_BOARD or self.player == 0 else 23-self.end
        if self.bars:
            steps.append(Step(player=int(not self.player), start=e, end=Action.BAR))
        steps.append(Step(player=int(self.player), start=s, end=e))
        return steps

    def __str__(self):
        return str(self.get_raw_steps())

    def __repr__(self):
        return str(self.get_raw_steps())