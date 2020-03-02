from abc import ABC, abstractmethod
import random
import numpy as np
from arm import Arm
from copy import deepcopy
from enum import Enum
from board import WHITE, BLACK

class Agent(ABC):
    """
    Abstract base class for agents.
    """

    def __init__(self, player):
        """
            
        :param player: WHITE (0) or BLACK (1)
        """
        self.player = player

    @abstractmethod
    def get_move(self, game, possible_moves):
        """
        Given a game state and a dict of features mapping to possible moves (see Board.get_possible_moves), select a 
        move.
        
        :param game: Game object. 
        :param possible_moves: List of tuples of Actions.
        :return: Tuple of Actions.
        """
        pass


class Difficulty(Enum):
    EASY = 0,
    MEDIUM = 1,
    HARD = 2


class TDAgent(Agent):
    """
    Agent that uses an EvaluationModel to help select its moves.
    """

    def __init__(self, player, model, computer_vision=None, difficulty=Difficulty.HARD):
        """
        
        :param player: See Agent class.
        :param model: EvaluationModel object.
        :param computer_vision: Vision object. Leave as None if using TDAgent for training/evaluating.
        :param difficulty: Difficulty enum.
        """
        super().__init__(player)
        self.model = model
        self.name = "Computer"
        self.difficulty = difficulty

        self.computer_vision = computer_vision
        if self.computer_vision:
            self.robot_arm = Arm()
            self.robot_arm.move_out_of_way()

    def get_move(self, game, possible_moves):
        if not possible_moves:
            return None

        if self.difficulty == Difficulty.HARD:
            # Return the best move possible.

            p_best = 0
            features_best = None
            for features in possible_moves:
                # p is the likelihood of BLACK winning given a game state.
                # The features are from the perspective of opponent.
                # We want to minimise the likelihood of the opponent winning.
                # If this agent is WHITE, then the opponent is BLACK so want to minimise p.
                # If this agent is BLACK, then the opponent is WHITE so want to maximise p.

                p = self.model(features)[0].item()
                p = 1. - p if self.player == WHITE else p
                if p > p_best:
                    p_best = p
                    features_best = features

            best_move = possible_moves[features_best]

        else:
            # Return the 75th or 50th percentile move if MEDIUM difficulty or EASY difficult respectively.

            p_features_list = []
            for features in possible_moves:
                p = self.model(features)[0].item()
                p = 1. - p if self.player == WHITE else p
                p_features_list.append((p, features))
            p_features_list.sort(key=lambda x: x[0])
            if self.difficulty == Difficulty.EASY:
                percentile = 0.5
            elif self.difficulty == Difficulty.MEDIUM:
                percentile = 0.75
            else:
                percentile = 1  # Fallback
            index = int(len(p_features_list) * percentile)
            best_move = possible_moves[p_features_list[index][1]]

        if self.computer_vision:
            steps = []
            for action in best_move:
                steps += action.get_raw_steps()

            for step in steps:
                # Printing the computers move
                print("Computer move from: " + str(step.start) + " to " + str(step.end))
                # Taking an image with the camera, request
                success = False
                while not success:
                    try:
                        (x1, y1), c2 = self.computer_vision.get_move(step)
                        x1 = 220 - x1 * 220
                        y1 = 220 * y1
                        if c2 == "OFF":
                            result = ((x1, y1), c2)
                        else:
                            x2, y2 = c2
                            x2 = 220 - x2 * 220
                            y2 = y2 * 220
                            result = ((x1, y1), (x2, y2))

                        self.robot_arm.move_piece(result)
                        self.robot_arm.move_out_of_way()
                        print(result)
                        success = True
                    except Exception as e:
                        input("Piece detection problem: Take image again... ")

        return best_move


class HumanAgent(Agent):
    """
    Agent for the human player.
    """

    def __init__(self, player, computer_vision):
        super().__init__(player)
        self.name = "Human"
        self.computer_vision = computer_vision

    def get_move(self, game, possible_moves):
        if len(possible_moves) == 0:
            print("No moves possible")
            return None

        while True:
            # input("Please type anything once you've played your move.")

            cv_output = self.computer_vision.take_turn()

            new_board = deepcopy(game.board)
            new_board.apply_cv_update(cv_output)
            new_board_features = new_board.get_features(not self.player)
            # print(new_board.points)
            # print(new_board.bar)
            if new_board_features in possible_moves:
                return possible_moves[new_board_features]
            print("Invalid move. Please try again... ")


class PubevalAgent(Agent):
    """
    Agent that uses the Pubeval model to help select its moves.
    Source: https://bkgm.com/rgb/rgb.cgi?view+610
    """
    def __init__(self, player):
        super().__init__(player)
        self.name = "Pubeval"

    wr = np.array(
        [0.00000, -0.17160, 0.27010, 0.29906, -0.08471, 0.00000, -1.40375, -1.05121, 0.07217, -0.01351, 0.00000,
         -1.29506, -2.16183, 0.13246, -1.03508, 0.00000, -2.29847, -2.34631, 0.17253, 0.08302, 0.00000, -1.27266,
         -2.87401, -0.07456, -0.34240, 0.00000, -1.34640, -2.46556, -0.13022, -0.01591, 0.00000, 0.27448, 0.60015,
         0.48302, 0.25236, 0.00000, 0.39521, 0.68178, 0.05281, 0.09266, 0.00000, 0.24855, -0.06844, -0.37646, 0.05685,
         0.00000, 0.17405, 0.00430, 0.74427, 0.00576, 0.00000, 0.12392, 0.31202, -0.91035, -0.16270, 0.00000, 0.01418,
         -0.10839, -0.02781, -0.88035, 0.00000, 1.07274, 2.00366, 1.16242, 0.22520, 0.00000, 0.85631, 1.06349, 1.49549,
         0.18966, 0.00000, 0.37183, -0.50352, -0.14818, 0.12039, 0.00000, 0.13681, 0.13978, 1.11245, -0.12707, 0.00000,
         -0.22082, 0.20178, -0.06285, -0.52728, 0.00000, -0.13597, -0.19412, -0.09308, -1.26062, 0.00000, 3.05454,
         5.16874, 1.50680, 5.35000, 0.00000, 2.19605, 3.85390, 0.88296, 2.30052, 0.00000, 0.92321, 1.08744, -0.11696,
         -0.78560, 0.00000, -0.09795, -0.83050, -1.09167, -4.94251, 0.00000, -1.00316, -3.66465, -2.56906, -9.67677,
         0.00000, -2.77982, -7.26713, -3.40177, -12.32252, 0.00000, 3.42040])

    wc = np.array(
        [0.25696, -0.66937, -1.66135, -2.02487, -2.53398, -0.16092, -1.11725, -1.06654, -0.92830, -1.99558, -1.10388,
         -0.80802, 0.09856, -0.62086, -1.27999, -0.59220, -0.73667, 0.89032, -0.38933, -1.59847, -1.50197, -0.60966,
         1.56166, -0.47389, -1.80390, -0.83425, -0.97741, -1.41371, 0.24500, 0.10970, -1.36476, -1.05572, 1.15420,
         0.11069, -0.38319, -0.74816, -0.59244, 0.81116, -0.39511, 0.11424, -0.73169, -0.56074, 1.09792, 0.15977,
         0.13786, -1.18435, -0.43363, 1.06169, -0.21329, 0.04798, -0.94373, -0.22982, 1.22737, -0.13099, -0.06295,
         -0.75882, -0.13658, 1.78389, 0.30416, 0.36797, -0.69851, 0.13003, 1.23070, 0.40868, -0.21081, -0.64073,
         0.31061, 1.59554, 0.65718, 0.25429, -0.80789, 0.08240, 1.78964, 0.54304, 0.41174, -1.06161, 0.07851, 2.01451,
         0.49786, 0.91936, -0.90750, 0.05941, 1.83120, 0.58722, 1.28777, -0.83711, -0.33248, 2.64983, 0.52698, 0.82132,
         -0.58897, -1.18223, 3.35809, 0.62017, 0.57353, -0.07276, -0.36214, 4.37655, 0.45481, 0.21746, 0.10504,
         -0.61977, 3.54001, 0.04612, -0.18108, 0.63211, -0.87046, 2.47673, -0.48016, -1.27157, 0.86505, -1.11342,
         1.24612, -0.82385, -2.77082, 1.23606, -1.59529, 0.10438, -1.30206, -4.11520, 5.62596, -2.75800])

    def setx(self, pos):
        x = np.zeros(122)
        for j in range(1, 25):
            n = pos[25 - j]
            jm1 = j - 1
            if n != 0:
                if n == -1:
                    x[5 * jm1 + 0] = 1.
                if n == 1:
                    x[5 * jm1 + 1] = 1.
                if n >= 2:
                    x[5 * jm1 + 2] = 1.
                if n == 3:
                    x[5 * jm1 + 3] = 1.
                if n >= 4:
                    x[5 * jm1 + 4] = float(n - 3) / 2.

        x[120] = -float(pos[0]) / 2.
        x[121] = float(pos[26]) / 15.
        return x

    def checkrace(self, pos):
        p1pos = np.where(pos[1:25] > 0)[0]
        p2pos = np.where(pos[1:25] < 0)[0]
        if (len(p2pos) == 0) | (len(p1pos) == 0):
            return True
        if p1pos[- 1] < p2pos[0]:
            return True
        return False

    def pubeval(self, race, pos):
        if pos[26] == 15:
            return 99999999.
        x = self.setx(pos)
        return np.dot(self.wr, x) if race else np.dot(self.wc, x)

    def get_move(self, game, possible_moves):
        if not possible_moves:
            return None
        possible_moves = list(possible_moves.values())
        na = len(possible_moves)
        va = np.zeros(na)
        race = self.checkrace(game.board.get_pubeval_pos())
        for i in range(0, na):
            game.board.apply_move(possible_moves[i])
            va[i] = self.pubeval(race, game.board.get_pubeval_pos())
            game.board.apply_move(possible_moves[i], undo=True)
        return possible_moves[np.argmax(va)]


class RandomAgent(Agent):
    """
    Agent that selects moves at random.
    """

    def __init__(self, player):
        super().__init__(player)
        self.name = "Randomiser"

    def get_move(self, game, possible_moves):
        if possible_moves:
            return random.choice(list(possible_moves.values()))
        return None
