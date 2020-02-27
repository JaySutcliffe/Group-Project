import numpy as np
from action import Action

class Board:

    def __init__(self):
        self.points = [[0, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2]
                       for _ in range(2)]
        self.bar = [0, 0]
        self.off = [0, 0]
        self.homed = [5, 5]

    def apply_move(self, move, undo=False):
        if move:
            for action in move:
                self.apply_action(action, undo)

    def apply_action(self, action, undo=False):
        delta = 1 if not undo else -1
        if action.start == Action.BAR:
            self.bar[action.player] -= delta
        else:
            self.points[action.player][action.start] -= delta
        if action.end == Action.OFF_BOARD:
            self.off[action.player] += delta
        else:
            if action.bars:
                self.bar[not action.player] += delta
                self.points[not action.player][23-action.end] -= delta
                if 18 <= action.end <= 23:
                    self.homed[not action.player] -= delta
            self.points[action.player][action.end] += delta
            if (action.start == Action.BAR or action.start >= 6) and 0 <= action.end <= 5:
                self.homed[action.player] += delta

    def get_possible_moves(self, player, rolls):
        possible_moves = dict()

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
            if current_move:
                features = self.get_features(not player)
                possible_moves[features] = current_move
            return

        roll = rolls[0]

        possible_ends = range(24-roll, 25-roll) if self.bar[player] > 0 else range(0, 24-roll)

        for end in possible_ends:
            if self.points[not player][23-end] >= 2:
                continue
            if self.bar[player] > 0:
                action = Action(player, Action.BAR, end, roll)
            else:
                start = end + roll
                if self.points[player][start] <= 0:
                    continue
                action = Action(player, start, end, roll)
            action.bars = self.points[not player][23-end] == 1
            self.apply_action(action)
            self.fill_possible_moves(player, rolls[1:], current_move + (action,), possible_moves)
            self.apply_action(action, undo=True)

        if self.homed[player] == 15:
            if self.points[player][roll-1] > 0:
                action = Action(player, roll-1, Action.OFF_BOARD, roll)
            else:
                if sum(self.points[player][roll:6]) == 0:
                    flag = False
                    for i in range(roll-2, -1, -1):
                        if self.points[player][i] > 0:
                            action = Action(player, i, Action.OFF_BOARD, roll)
                            flag = True
                            break
                    if not flag:
                        return
                else:
                    return
            self.apply_action(action)
            self.fill_possible_moves(player, rolls[1:], current_move + (action,), possible_moves)
            self.apply_action(action, undo=True)

    def get_features(self, player):
        features = []
        for p in range(2):
            for point in (self.points[p] if p == 0 else reversed(self.points[p])):
                checkers = [0., 0., 0., 0.]
                for i in range(point):
                    if i < 3:
                        checkers[i] = 1.
                    else:
                        checkers[3] += 0.5
                features += checkers
            features.append(float(self.bar[p]) / 2.)
            features.append(float(self.off[p]) / 15.)
        features += [float(not player), float(player)]
        return tuple(features)

    def get_pubeval_pos(self):
        pos = [-self.bar[1]] #0
        for i in range(24): #1-24
            if self.points[0][i] != 0:
                pos.append(self.points[0][i])
            elif self.points[1][23-i] != 0:
                pos.append(-self.points[1][23-i])
            else:
                pos.append(0)
        pos.append(self.bar[0]) #25
        pos.append(self.off[0]) #26
        pos.append(-self.off[1]) #27
        return np.array(pos)

    def apply_cv_update(self, cv_output):
        bar_white = cv_output[0]
        bar_black = cv_output[1]
        add = cv_output[2]
        sub = cv_output[3]

        for tup in sub:
            add.append((tup[0], -tup[1], tup[2]))
        self.bar = [bar_white, bar_black]

        for change in add:
            colour = change[0]
            player = 0 if colour == "W" else 1
            amount = change[1]
            spike = change[2]
            spike = spike if player == 1 else 23-spike
            self.points[player][spike] += amount

        self.off = [15-sum(self.points[0])-self.bar[0],
                    15-sum(self.points[1])-self.bar[1]]
