import random
from action import Action
from board import Board
import numpy as np

class Game:

    def __init__(self, agents):
        self.board = Board()
        self.agents = agents
        self.player_agent_map = agents.copy()
        self.current_player = 0

    # copied
    def extract_features(self, player):
        features = []
        for p in range(len(self.player_agent_map)):
            for point in self.board.points:
                feats = [0., 0., 0., 0.]
                if point[p] > 0:
                    for i in range(point[p]):
                        if i < 3:
                            feats[i] = 1
                        else:
                            feats[3] += 0.5
                features += feats
            features.append(float(self.board.bar[p]) / 2.)
            features.append(float(self.board.off[p]) / 15.)
        features += [float(not player), float(player)]
        assert len(features) == 198, print("Should be 198 instead of {}".format(len(features)))
        return features

    def starting_roll(self):
        roll = [0, 0]
        while roll[0] == roll[1]:
            roll = self.roll_dice()
        if roll[0] > roll[1]:
            self.current_player = 0
        else:
            self.current_player = 1
        return roll

    def init_players(self, starting_agent_index):
        self.agents[starting_agent_index].set_player(0)
        self.agents[not starting_agent_index].set_player(1)
        self.player_agent_map = [self.agents[starting_agent_index], self.agents[not starting_agent_index]]

    def winner(self):
        if self.board.off[0] == 15:
            return (0, self.player_agent_map[0])
        elif self.board.off[1] == 15:
            return (1, self.player_agent_map[1])
        return False

    def next_turn(self, player, roll=None):
        if roll is None:
            roll = self.roll_dice()
        possible_moves = self.get_possible_moves(player, roll)
        move = self.player_agent_map[player].get_move(self, possible_moves)
        #print("Move: " + str(move))
        self.apply_move(move)

    def play(self):
        roll1 = self.starting_roll()
        self.next_turn(self.current_player, roll1)
        while not self.winner():
            self.current_player = not self.current_player
            self.next_turn(self.current_player)
        return self.winner()

    @staticmethod
    def roll_dice():
        return [random.randint(1, 6), random.randint(1, 6)]

    def check_possible_action(self, action):
        if action.start != Action.BAR \
                and action.end != Action.OFF_BOARD \
                and ((not (0 <= action.start <= 23) or not (0 <= action.end <= 23)) or abs(action.start - action.end) != action.roll):
            return False
        if self.board.bar[action.player] > 0 and action.start != Action.BAR:
            return False
        if self.board.homed[action.player] < 15 and action.end == Action.OFF_BOARD:
            return False
        if action.start != Action.BAR and self.board.points[action.start][action.player] <= 0:
            return False
        if action.end != Action.OFF_BOARD and self.board.points[action.end][not action.player] >= 2:
            return False
        return True

    def apply_move(self, move, undo=False):
        if move:
            for action in move:
                self.apply_action(action, undo)

    def apply_action(self, action, undo=False):
        delta = 1 if not undo else -1
        if action.start == Action.BAR:
            self.board.bar[action.player] -= delta
        else:
            self.board.points[action.start][action.player] -= delta
        if action.end == Action.OFF_BOARD:
            self.board.off[action.player] += delta
        else:
            if action.bars:
                self.board.bar[not action.player] += delta
                self.board.points[action.end][not action.player] -= delta
                if action.player == 1 and 0 <= action.end <= 5 or action.player == 0 and 18 <= action.end <= 23:
                    self.board.homed[not action.player] -= delta
            self.board.points[action.end][action.player] += delta
            if action.player == 0 and (action.start == Action.BAR or action.start >= 6) and 0 <= action.end <= 5\
                    or action.player == 1 and (action.start == Action.BAR or action.start <= 17) and 18 <= action.end <= 23:
                self.board.homed[action.player] += delta

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
            if self.board.bar[player] > 0:
                possible_range = range(24-roll, 24-roll+1)
            else:
                possible_range = range(0, 24-roll)
        else:
            if self.board.bar[player] > 0:
                possible_range = range(roll-1, roll)
            else:
                possible_range = range(roll, 24)

        for i in possible_range:
            if self.board.bar[player] > 0:
                action = Action(player, Action.BAR, i, roll)
            else:
                action = Action(player, i + (1-2*player)*roll, i, roll)
            if self.board.points[action.end][not action.player] == 1 and self.board.points[action.end][action.player] == 0:
                action.bars = True
            if self.check_possible_action(action):
                board_copy = [self.board.points.copy(), self.board.bar.copy(), self.board.off.copy()]
                self.apply_action(action)
                self.fill_possible_moves(player, rolls[1:], current_move + (action,), possible_moves)
                self.apply_action(action, undo=True)
                if [self.board.points, self.board.bar, self.board.off] != board_copy:
                    print("undo not working")
                    exit()

        if self.board.homed[player] == 15:
            if player == 0:
                start = roll - 1
            else:
                start = 24 - roll
            action = Action(player, start, Action.OFF_BOARD, roll)
            if self.check_possible_action(action):
                board_copy = [self.board.points.copy(), self.board.bar.copy(), self.board.off.copy()]
                self.apply_action(action)
                self.fill_possible_moves(player, rolls[1:], current_move + (action,), possible_moves)
                self.apply_action(action, undo=True)
                if [self.board.points, self.board.bar, self.board.off] != board_copy:
                    print("undo not working")
                    exit()
