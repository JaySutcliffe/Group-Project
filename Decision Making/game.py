import random
from board import Board
from agents import TDAgent, HumanAgent

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

    def next_turn(self, player, roll=None, pretty=False):
        if roll is None:
            roll = self.roll_dice()
        possible_moves = self.board.get_possible_moves(player, roll)
        move = self.agents[player].get_move(self, possible_moves)
        self.board.apply_move(move)
        if pretty:
            print("Move played: " + str(move))

    def play(self):
        roll1, current_player = self.starting_roll()
        self.next_turn(current_player, roll1)
        while not self.winner():
            current_player = not current_player
            self.next_turn(current_player)
        return self.winner()

    def play_real(self):
        print(self.agents[0].name + " is WHITE")
        print(self.agents[1].name + " is BLACK")
        roll1, current_player = self.starting_roll()
        print(self.agents[current_player].name + " starts")
        print("Board state:")
        print("\tSpikes array:" + str(game.board.points))
        print("\tBar: " + str(game.board.bar))
        print("\tOff: " + str(game.board.off))
        print("Dice roll: " + str(roll1))
        self.next_turn(current_player, roll=roll1, pretty=True)
        while not self.winner():
            current_player = not current_player
            print()
            print(self.agents[current_player].name + "'s turn")
            print("Board state:")
            print("\tSpikes array:" + str(game.board.points))
            print("\tBar: " + str(game.board.bar))
            print("\tOff: " + str(game.board.off))
            roll = self.roll_dice()
            print("Dice roll: " + str(roll))
            self.next_turn(current_player, roll=roll, pretty=True)
        print(self.winner()[1].name + " wins!")
        return self.winner()

    @staticmethod
    def roll_dice():
        return [random.randint(1, 6), random.randint(1, 6)]

if __name__ == "__main__":
    from evaluator import EvaluationModel
    net = EvaluationModel(hidden_units=40, alpha=0.1, lamda=None)
    net.load(checkpoint_path="./saved_models/exp4/exp1_20200221_1714_18_357821_188000.tar")
    td_agent = TDAgent(0, net)
    human_agent = HumanAgent(1)
    game = Game([td_agent, human_agent])
    game.play_real()
