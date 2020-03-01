class Action:
    BAR = "BAR"
    OFF_BOARD = "OFF"

    def __init__(self, player, start, end, roll, bars=False):
        self.player = player
        self.start = start
        self.end = end
        self.roll = roll
        self.bars = bars

    def print_action(self):
        print("Player: " + str(self.player)
              + ", Start: " + str(self.start)
              + ", End: " + str(self.end)
              + ", Roll: " + str(self.roll)
              + ", Bars: " + str(self.bars))
