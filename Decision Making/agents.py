from abc import ABC, abstractmethod
import random


class Agent(ABC):

    @abstractmethod
    def get_move(self, game, possible_moves):
        pass


class TDAgent(Agent):

    def __init__(self, player, model):
        super().__init__()
        self.player = player
        self.model = model

    def get_move(self, game, possible_moves):
        if not possible_moves:
            return None

        v_best = 0
        m_best = possible_moves[0]

        for m in possible_moves:
            game.apply_move(m)
            features = game.get_features(not self.player)
            v = self.model(features)[0].item()
            v = 1. - v if self.player == 0 else v
            #print(str(self.player) + ", " + str(v))
            if v > v_best:
                v_best = v
                m_best = m
            game.apply_move(m, undo=True)

        return m_best


class HumanAgent(Agent):

    def get_move(self, game, possible_moves):
        pass


class RandomAgent(Agent):

    def __init__(self):
        super().__init__()

    def get_move(self, game, possible_moves):
        if possible_moves:
            return random.choice(possible_moves)
        return None
