import random

import vision
from agents import TDAgent, HumanAgent, Difficulty
from board import Board, WHITE, BLACK


class Game:
    """
    Instance of a game between two agents (i.e. players).
    """

    def __init__(self, agents):
        """
        Constructs a game instance.
        
        :param agents: List of two Agents. agents[0] plays as WHITE, agents[1] plays as BLACK.
        """
        self.board = Board()
        self.agents = agents

    @staticmethod
    def roll_dice():
        return [random.randint(1, 6), random.randint(1, 6)]

    def first_roll(self):
        starting_roll = [0, 0]
        while starting_roll[0] == starting_roll[1]:
            starting_roll = self.roll_dice()
        if starting_roll[0] > starting_roll[1]:
            starting_player = WHITE
        else:
            starting_player = BLACK
        return starting_roll, starting_player

    def winner(self):
        if self.board.off[WHITE] == 15:
            return WHITE
        elif self.board.off[1] == 15:
            return BLACK
        return None

    def next_turn(self, player, roll=None, pretty=False):
        if roll is None:
            roll = self.roll_dice()

        possible_moves = self.board.get_possible_moves(player, roll)
        move = self.agents[player].get_move(self, possible_moves)
        self.board.apply_move(move)

        if pretty and move:
            print("Moves made: ")
            for m in move:
                print(str(m.start) + " to " + str(m.end))

    def play(self, starting_roll=None, starting_player=None):
        if starting_roll is None or starting_player is None:
            starting_roll, starting_player = self.first_roll()

        self.next_turn(starting_player, starting_roll)

        while self.winner() is None:
            starting_player = not starting_player
            self.next_turn(starting_player)

        return self.winner()

    def play_real(self, roll1=None, current_player=None):
        print(self.agents[WHITE].name + " is WHITE")
        print(self.agents[BLACK].name + " is BLACK")
        if roll1 is None or current_player is None:
            roll1, current_player = self.first_roll()
        print(self.agents[current_player].name + " starts")

        # Logging the details of the current board state
        # before a turn is made
        log = open("logs/play log.txt", "w")
        log.write(self.agents[current_player].name + "'s turn\n")
        log.write("Board state:\n")
        log.write("Spikes white: " + str(game.board.points[WHITE]) + "\n")
        log.write("Spikes black: " + str(game.board.points[BLACK]) + "\n")
        log.write("Bar white: " + str(game.board.bar[WHITE]) + "\n")
        log.write("Bar black: " + str(game.board.bar[BLACK]) + "\n")
        log.write("Off white: " + str(game.board.off[WHITE]) + "\n")
        log.write("Off black: " + str(game.board.off[BLACK]) + "\n")
        log.close()

        # print("Board state:")
        # print("\tSpikes array:" + str(game.board.points))
        # print("\tBar: " + str(game.board.bar))
        # print("\tOff: " + str(game.board.off))

        if self.agents[current_player].name == "Human":
            print("You rolled a: " + str(roll1))
        else:
            print("The computer rolled a: " + str(roll1))

        self.next_turn(current_player, roll=roll1, pretty=True)
        while self.winner() is None:
            current_player = not current_player

            # Logging the details of the current board stat
            log = open("logs/play log.txt", "w")
            log.write(self.agents[current_player].name + "'s turn\n")
            log.write("Board state:\n")
            log.write("Spikes white: " + str(game.board.points[WHITE]) + "\n")
            log.write("Spikes black: " + str(game.board.points[BLACK]) + "\n")
            log.write("Bar white: " + str(game.board.bar[WHITE]) + "\n")
            log.write("Bar black: " + str(game.board.bar[BLACK]) + "\n")
            log.write("Off white: " + str(game.board.off[WHITE]) + "\n")
            log.write("Off black: " + str(game.board.off[BLACK]) + "\n")
            log.close()

            print()
            print(self.agents[current_player].name + "'s turn")

            # print("Board state:")
            # print("\tSpikes array:" + str(game.board.points))
            # print("\tBar: " + str(game.board.bar))
            # print("\tOff: " + str(game.board.off))
            roll = self.roll_dice()

            if self.agents[current_player].name == "Human":
                print("You rolled a: " + str(roll))
            else:
                print("The computer rolled a: " + str(roll))

            self.next_turn(current_player, roll=roll, pretty=True)
        print(self.agents[self.winner()].name + " wins!")
        return self.winner()


    def play_real_from_given_state(self, points, bar, agents, starting_player, starting_roll):
        self.agents = agents
        self.board.set_state(points, bar)
        self.play_real(starting_roll, starting_player)

if __name__ == "__main__":
    from evaluator import EvaluationModel

    model = EvaluationModel(num_hidden_units=(40,),
                            starting_alpha=0.1, starting_lamda=0.9,
                            min_alpha=0.1, min_lamda=0.7,
                            alpha_decay=1, lamda_decay=0.96,
                            alpha_decay_interval=1, lamda_decay_interval=3e4)
    model.load(checkpoint_path="./stored_models/final/final_20200302_0326_50_865023_728001.tar")

    difficulty_input = ""
    while difficulty_input not in ["E", "M", "H"]:
        difficulty_input= input("Select difficulty level: EASY (E), MEDIUM (M), HARD (H)")
        if difficulty_input == "E":
            difficulty = Difficulty.EASY
        elif difficulty_input == "M":
            difficulty = Difficulty.MEDIUM
        elif difficulty_input == "H":
            difficulty = Difficulty.HARD

    v = vision.Vision()
    td_agent = TDAgent(WHITE, model, v, difficulty)
    human_agent = HumanAgent(BLACK, v)
    agents_list = [td_agent, human_agent]
    game = Game(agents_list)

    set_start_state = False
    if set_start_state:
        start_points = [
            [3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 3, 3, 2, 2, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        start_bar = [0, 2]
        start_roll = [3, 1]
        start_player = BLACK
        game.play_real_from_given_state(start_points, start_bar, agents_list, start_roll, start_player)
    else:
        game.play_real()
