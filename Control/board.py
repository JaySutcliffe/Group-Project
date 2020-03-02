import numpy as np
from action import Action

WHITE = 0
BLACK = 1

class Board:
    """
    Abstract representation of the board state.
    """

    def __init__(self):
        # self.points[WHITE] stores the number of WHITE checkers on WHITE's points 1 to 24 (from index 0 to 23 respectively).
        # self.points[BLACK] stores the number of BLACK checkers on BLACK's points 1 to 24 (from index 0 to 23 respectively).
        # The physical spike represented by self.points[WHITE][n] is the same as that represented by self.points[BLACK][23-n].
        self.points = [[0, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2]
                       for _ in range(2)]

        # self.bar[WHITE] stores the number of WHITE checkers on the bar. Similarly for BLACK.
        self.bar = [0, 0]

        # self.off[WHITE] stores the number of WHITE checkers that have been beared off.
        self.off = [0, 0]

        # self.homed[WHITE] stores the number of WHITE checkers that are in WHITE's home board or that have been beared off.
        self.homed = [5, 5]

    def set_state(self, points, bar):
        self.points = points
        self.bar = bar
        self.off = [15 - sum(points[p]) - bar[p] for p in range(2)]
        self.homed = [sum(points[p][0:6]) + self.off[p] for p in range(2)]


    def apply_move(self, move, undo=False):
        if move:
            for action in move:
                self.apply_action(action, undo)

    def apply_action(self, action, undo=False):
        """
        Update the board state after an action.
        
        :param action: Action.
        :param undo: Boolean. Flag for whether the action should be unperformed or performed.
        """

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
                self.points[not action.player][23 - action.end] -= delta
                if 18 <= action.end <= 23:
                    self.homed[not action.player] -= delta
            self.points[action.player][action.end] += delta
            if (action.start == Action.BAR or action.start >= 6) and 0 <= action.end <= 5:
                self.homed[action.player] += delta

    def get_possible_moves(self, player, rolls):
        """
        Generate all valid moves for the player given a set of dice rolls. A move is a tuple of Actions.
        
        :param player: WHITE (0) or BLACK (1).
        :param rolls: List of 2 integers between 1 and 6 inclusive. 
        :return: Dict of features (tuple) mapping to moves (tuples of Actions). 
            The features are the features for the EvaluationModel for the game state after the move is applied.
        """

        possible_moves = dict()

        if rolls[0] == rolls[1]:
            # Double rolls are duplicated so 4 rolls are effectively to be played.
            rolls = rolls.copy()
            rolls.extend(rolls)

            # If there are no possible moves using all 4 rolls, try using 3, then 2, then 1.
            while len(rolls) > 0 and not possible_moves:
                self.fill_possible_moves(player, rolls, (), possible_moves)
                rolls = rolls[1:]
        else:
            # Need to consider both orderings of rolls as some moves can only be done in one of the orders.
            self.fill_possible_moves(player, rolls, (), possible_moves)
            self.fill_possible_moves(player, [rolls[1], rolls[0]], (), possible_moves)

            # If there are no possible moves using both rolls, try using the larger roll, then the smaller one.
            if not possible_moves:
                self.fill_possible_moves(player, [max(rolls)], (), possible_moves)
                if not possible_moves:
                    self.fill_possible_moves(player, [min(rolls)], (), possible_moves)

        return possible_moves

    def fill_possible_moves(self, player, rolls, current_move, possible_moves):
        """
        Populates the possible_moves dict with possible moves.
        
        :param player: WHITE (0) or BLACK (1).
        :param rolls: List of integers between 1 and 6 inclusive. The rolls remaining.
        :param current_move: Tuple of Actions. The actions making up the move so far (i.e. from the previous rolls)
        :param possible_moves: Dict of features (tuple) mapping to moves (tuples of Actions). See get_possible_moves
        """
        if not rolls:
            if current_move:
                # If all rolls have been played a move exists, apply the move and get the features from the opponent's
                # perspective.
                features = self.get_features(not player)
                possible_moves[features] = current_move
            return

        roll = rolls[0]

        # Range of points where the player can potentially move checkers to given the dice roll and the bar state.
        possible_ends = range(24 - roll, 25 - roll) if self.bar[player] > 0 else range(0, 24 - roll)

        for end in possible_ends:
            # Cannot move checkers to a point with 2 or more opposing checkers.
            if self.points[not player][23 - end] >= 2:
                continue

            # Must move checkers from bar if there are checkers on the bar.
            if self.bar[player] > 0:
                action = Action(player, Action.BAR, end, roll)
            else:
                start = end + roll
                if self.points[player][start] <= 0:
                    continue
                action = Action(player, start, end, roll)

            # Check if the action knocks off an opponent's checker.
            action.bars = self.points[not player][23 - end] == 1

            # Apply the action and recurse and then undo the action to revert board state.
            self.apply_action(action)
            self.fill_possible_moves(player, rolls[1:], current_move + (action,), possible_moves)
            self.apply_action(action, undo=True)

        # Check if bearing off is possible and attempt it
        if self.homed[player] == 15:
            if self.points[player][roll - 1] > 0:
                action = Action(player, roll - 1, Action.OFF_BOARD, roll)
            else:
                if sum(self.points[player][roll:6]) == 0:
                    flag = False
                    for i in range(roll - 2, -1, -1):
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
        """
        Extract the features encoding the game state.
        The features are as described in: 
            https://web.stanford.edu/group/pdplab/pdphandbook/handbookch10.html#x26-1370009.3.2
        
        :param player: WHITE (0) or BLACK (1). Player whose turn it is.
        :return: Tuple of floats. The features.
        """

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
        """
        Convert the board state to the representation used by pubeval.
        The representation is as described in: https://bkgm.com/rgb/rgb.cgi?view+610 (where it is called pos)
        
        :return: Numpy array of integers.
        """
        pos = [-self.bar[1]]  # 0
        for i in range(24):  # 1-24
            if self.points[0][i] != 0:
                pos.append(self.points[0][i])
            elif self.points[1][23 - i] != 0:
                pos.append(-self.points[1][23 - i])
            else:
                pos.append(0)
        pos.append(self.bar[0])  # 25
        pos.append(self.off[0])  # 26
        pos.append(-self.off[1])  # 27
        return np.array(pos)

    def apply_cv_update(self, cv_output):
        """
        Update the board state given a set of board changes made by the human.
        
        :param cv_output: Tuple. See below for more details.
        """

        # An integer representing the total number of white pieces that have been knocked out and are placed in the middle of the board.
        bar_white = cv_output[1]

        # An integer representing the total number of black pieces that have been knocked out.
        bar_black = cv_output[0]

        # A list of tuples of the form (colour (“W”/”B”), amount added, spike added to)
        add = cv_output[2]

        # A list of tuples of the form (colour (“W”/”B”), amount removed, spike removed from)
        sub = cv_output[3]

        # Convert subs to adds
        for tup in sub:
            add.append((tup[0], -tup[1], tup[2]))
        self.bar = [bar_white, bar_black]

        for change in add:
            colour = change[0]
            player = 0 if colour == "W" else 1
            amount = change[1]
            spike = change[2]
            spike = spike if player == 1 else 23 - spike
            self.points[player][spike] += amount

        self.off = [15 - sum(self.points[0]) - self.bar[0],
                    15 - sum(self.points[1]) - self.bar[1]]
