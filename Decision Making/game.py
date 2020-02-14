import random
from action import Action


class Game:

    def __init__(self, agents):
        self.points = [
            [0, 2],
            [0, 0],
            [0, 0],
            [0, 0],
            [0, 0],
            [5, 0],
            [0, 0],
            [3, 0],
            [0, 0],
            [0, 0],
            [0, 0],
            [0, 5],
            [5, 0],
            [0, 0],
            [0, 0],
            [0, 0],
            [0, 3],
            [0, 0],
            [0, 5],
            [0, 0],
            [0, 0],
            [0, 0],
            [0, 0],
            [2, 0],
        ]
        self.bar = [0, 0]
        self.off = [0, 0]
        self.homed = [5, 5]
        self.agents = agents

    def get_features(self, player):
        features = []
        for p in range(len(self.agents)):
            for point in self.points:
                checkers = [0., 0., 0., 0.]
                if point[p] > 0:
                    for i in range(point[p]):
                        if i < 3:
                            checkers[i] = 1.
                        else:
                            checkers[3] += 0.5
                features += checkers
            features.append(float(self.bar[p]) / 2.)
            features.append(float(self.off[p]) / 15.)
        features += [float(not player), float(player)]
        return features

    def starting_roll(self):
        roll = [0, 0]
        while roll[0] == roll[1]:
            roll = self.roll_dice()
        if roll[0] > roll[1]:
            current_player = 0
        else:
            current_player = 1
        return roll, current_player

    def winner(self):
        if self.off[0] == 15:
            return 0, self.agents[0]
        elif self.off[1] == 15:
            return 1, self.agents[1]
        return False

    def next_turn(self, player, roll=None):
        if roll is None:
            roll = self.roll_dice()
        possible_moves = self.get_possible_moves(player, roll)
        move = self.agents[player].get_move(self, possible_moves)
        self.apply_move(move)

    def play(self):
        roll1, current_player = self.starting_roll()
        self.next_turn(current_player, roll1)
        while not self.winner():
            current_player = not current_player
            self.next_turn(current_player)
        return self.winner()

    @staticmethod
    def roll_dice():
        return [random.randint(1, 6), random.randint(1, 6)]

    def apply_move(self, move, undo=False):
        if move:
            for action in move:
                self.apply_action(action, undo)

    def apply_action(self, action, undo=False):
        delta = 1 if not undo else -1
        if action.start == Action.BAR:
            self.bar[action.player] -= delta
        else:
            self.points[action.start][action.player] -= delta
        if action.end == Action.OFF_BOARD:
            self.off[action.player] += delta
        else:
            if action.bars:
                self.bar[not action.player] += delta
                self.points[action.end][not action.player] -= delta
                if action.player == 1 and 0 <= action.end <= 5 or action.player == 0 and 18 <= action.end <= 23:
                    self.homed[not action.player] -= delta
            self.points[action.end][action.player] += delta
            if action.player == 0 and (action.start == Action.BAR or action.start >= 6) and 0 <= action.end <= 5 \
                    or action.player == 1 and (
                    action.start == Action.BAR or action.start <= 17) and 18 <= action.end <= 23:
                self.homed[action.player] += delta

    def get_possible_moves(self, player, rolls):
        possible_moves = list()

        if rolls[0] == rolls[1]:
            rolls = rolls.copy()
            rolls.extend(rolls)
            while len(rolls) > 0 and not possible_moves:
                self.fill_possible_moves(player, rolls, (), possible_moves)
                rolls = rolls[1:]
        else:
            self.fill_possible_moves(player, rolls, (), possible_moves)
            self.fill_possible_moves(player, [rolls[1], rolls[0]], (), possible_moves)
            if not possible_moves:
                self.fill_possible_moves(player, [max(rolls)], (), possible_moves)
                if not possible_moves:
                    self.fill_possible_moves(player, [min(rolls)], (), possible_moves)

        return possible_moves

    def fill_possible_moves(self, player, rolls, current_move, possible_moves):
        if not rolls:
            possible_moves.append(current_move)
            return

        roll = rolls[0]

        if player == 0:
            if self.bar[player] > 0:
                possible_range = range(24 - roll, 24 - roll + 1)
            else:
                possible_range = range(0, 24 - roll)
        else:
            if self.bar[player] > 0:
                possible_range = range(roll - 1, roll)
            else:
                possible_range = range(roll, 24)

        for end in possible_range:
            if self.points[end][not player] >= 2:
                continue
            if self.bar[player] > 0:
                action = Action(player, Action.BAR, end, roll)
            else:
                start = end + (1 - 2 * player) * roll
                if self.points[start][player] <= 0:
                    continue
                action = Action(player, start, end, roll)
            if self.points[action.end][not action.player] == 1 and self.points[action.end][action.player] == 0:
                action.bars = True
            self.apply_action(action)
            self.fill_possible_moves(player, rolls[1:], current_move + (action,), possible_moves)
            self.apply_action(action, undo=True)

        if self.homed[player] == 15:
            if player == 0:
                start = roll - 1
            else:
                start = 24 - roll
            action = Action(player, start, Action.OFF_BOARD, roll)
            if self.points[start][player] > 0:
                self.apply_action(action)
                self.fill_possible_moves(player, rolls[1:], current_move + (action,), possible_moves)
                self.apply_action(action, undo=True)
