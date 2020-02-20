import random
from board import Board

class Game:

    def __init__(self, agents):
        self.board = Board()
        self.agents = agents

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
        if self.board.off[0] == 15:
            return 0, self.agents[0]
        elif self.board.off[1] == 15:
            return 1, self.agents[1]
        return False

    def next_turn(self, player, roll=None):
        if roll is None:
            roll = self.roll_dice()
        possible_moves = self.board.get_possible_moves(player, roll)
        move = self.agents[player].get_move(self, possible_moves)
        self.board.apply_move(move)

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

