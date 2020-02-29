import random
import vision
from board import Board
from agents import TDAgent, HumanAgent, Difficulty

class Game:

    def __init__(self, agents):
        self.board = Board()
        self.agents = agents

    def play_real_from_given_state(self, points, bar, agents, player1, roll1):
        self.agents = agents
        self.board.points = points
        self.board.bar = bar
        self.board.off = [15-sum(points[p]) - bar[p] for p in range(2)]
        self.board.homed = [sum(points[p][0:6]) + self.board.off[p] for p in range(2)]
        self.play_real(roll1, player1)

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
        if pretty and move:
            print("Moves made: ")
            for m in move:
              print(str(m.start) + " to " + str(m.end))

    def play(self, roll1=None, current_player=None):
        if roll1 is None or current_player is None:
            roll1, current_player = self.starting_roll()
        self.next_turn(current_player, roll1)
        while not self.winner():
            current_player = not current_player
            self.next_turn(current_player)
        return self.winner()

    def play_real(self, roll1=None, current_player=None):
        print(self.agents[0].name + " is WHITE")
        print(self.agents[1].name + " is BLACK")
        if roll1 is None or current_player is None:
            roll1, current_player = self.starting_roll()
        print(self.agents[current_player].name + " starts")
       
        # Logging the details of the current board state
        # before a turn is made
        log = open("logs/play log.txt", "w") 
        log.write(self.agents[current_player].name + "'s turn\n")
        log.write("Board state:\n")
        log.write("Spikes white: " + str(game.board.points[0]) + "\n")
        log.write("Spikes black: " + str(game.board.points[1]) + "\n")
        log.write("Bar white: " + str(game.board.bar[0]) + "\n")
        log.write("Bar black: " + str(game.board.bar[1]) + "\n")
        log.write("Off white: " + str(game.board.off[0]) + "\n")
        log.write("Off black: " + str(game.board.off[1]) + "\n")
        log.close()
       
        # print("Board state:")
        # print("\tSpikes array:" + str(game.board.points))
        # print("\tBar: " + str(game.board.bar))
        # print("\tOff: " + str(game.board.off))
        
        if (self.agents[current_player].name == "Human"):
            print("You rolled a: " + str(roll1))
        else:
            print("The computer rolled a: " + str(roll1))
            
        
        self.next_turn(current_player, roll=roll1, pretty=True)
        while not self.winner():
            current_player = not current_player

            # Logging the details of the current board stat
            log = open("logs/play log.txt", "w") 
            log.write(self.agents[current_player].name + "'s turn\n")
            log.write("Board state:\n")
            log.write("Spikes white: " + str(game.board.points[0]) + "\n")
            log.write("Spikes black: " + str(game.board.points[1]) + "\n")
            log.write("Bar white: " + str(game.board.bar[0]) + "\n")
            log.write("Bar black: " + str(game.board.bar[1]) + "\n")
            log.write("Off white: " + str(game.board.off[0]) + "\n")
            log.write("Off black: " + str(game.board.off[1]) + "\n")
            log.close()
            
            print()
            print(self.agents[current_player].name + "'s turn")
         
            # print("Board state:")
            # print("\tSpikes array:" + str(game.board.points))
            # print("\tBar: " + str(game.board.bar))
            # print("\tOff: " + str(game.board.off))
            roll = self.roll_dice()
            
            if (self.agents[current_player].name == "Human"):
                print("You rolled a: " + str(roll))
            else:
                print("The computer rolled a: " + str(roll))
            
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
    v = vision.Vision()
    td_agent = TDAgent(0, net, v)
    human_agent = HumanAgent(1, v)
    playing_agents = [td_agent, human_agent]
    game = Game(playing_agents)

    set_start_state = False
    if set_start_state:
        starting_points = [
            [3,3,3,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,3,3,2,2,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ]
        starting_bar = [0,2]
        starting_roll = [3,1]
        starting_player = 1
        game.play_real_from_given_state(starting_points, starting_bar, playing_agents, starting_player, starting_roll)
    else:
        game.play_real()
