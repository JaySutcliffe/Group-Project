from abc import ABC, abstractmethod
import random

class Agent(ABC):

    def __init__(self, player=0):
        self.player = player

    def set_player(self, player):
        self.player = player

    @abstractmethod
    def get_move(self, game, possible_moves):
        pass

class TDAgent(Agent):

    def __init__(self, player, model):
        super().__init__(player)
        self.model = model
        self.name = "TD Agent"


    # copied
    def get_move(self, game, possible_moves):
        v_best = 0
        m_best = None

        for m in possible_moves:
            game.apply_move(m)
            features = game.extract_features(not self.player)
            v = self.model(features)
            v = 1. - v if self.player == 0 else v
            if v > v_best:
                v_best = v
                m_best = m
            game.apply_move(m, undo=True)

        return m_best

class HumanAgent(Agent):

    def __init__(self, player, name):
        super().__init__(player)
        self.name = name

    def get_move(self, game, possible_moves):
        if possible_moves:
            possible_moves = set(possible_moves)
            input_move = None
            while input_move not in possible_moves:
                raw_input_move = input("Please enter a valid move.")
                input_move = self.format_raw_input_move(raw_input_move)

        print("No moves are possible. You skip your turn.")
        return input_move

    def format_raw_input_move(self, raw_input_move):
        return None



class RandomAgent(Agent):

    def __init__(self, player):
        super().__init__(player)
        self.name = "Random Agent"

    def get_move(self, game, possible_moves):
        if possible_moves:
            return random.choice(possible_moves)
        return None
