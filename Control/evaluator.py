import datetime
import random
from collections import OrderedDict
from itertools import count

import numpy as np
import torch
import torch.nn as nn
from agents import TDAgent
from game import Game

torch.set_default_tensor_type('torch.DoubleTensor')


class EvaluationModel(nn.Module):
    """
    A neural network that evaluates a game state and returns the likelihood of BLACK winning.
    This is an implementation of Tesauro's TD-Gammon as described here:
    https://www.bkgm.com/articles/tesauro/tdl.html.
    """


    def __init__(self, num_inputs=198, num_hidden_units=(40,),
                 starting_alpha=0.1, starting_lamda=0.9,
                 min_alpha=0.1, min_lamda=0.7,
                 alpha_decay=1, lamda_decay=0.96,
                 alpha_decay_interval=1, lamda_decay_interval=3e4,
                 hidden_activation=nn.Sigmoid()):
        """
        Construct a new model.
        
        :param num_inputs: Integer. Number of units in the input layer.
        :param num_hidden_units: Tuple of integers. Number of units in each hidden layer.
        :param starting_alpha: Float. Initial value for alpha (the learning rate parameter).
        :param starting_lamda: Float. Initial value for lambda (the trace decay parameter). 
        :param min_alpha: Float. Minimum value for alpha (will not decay past this).
        :param min_lamda: Float. Minimum value for lambda (will not decay past this).
        :param alpha_decay: Float. How much alpha is multiplied by every alpha_decay_interval number of global steps.
        :param lamda_decay: Float. How much lambda is multiplied by every alpha_decay_interval number of global steps.
        :param alpha_decay_interval: Integer. See alpha_decay.
        :param lamda_decay_interval: Integer. See lamda_decay.
        :param hidden_activation: nn.Module. Activation function for the hidden layers.
        """

        super(EvaluationModel, self).__init__()
        self.starting_alpha = starting_alpha
        self.starting_lamda = starting_lamda
        self.min_alpha = min_alpha
        self.min_lamda = min_lamda
        self.alpha_decay = alpha_decay
        self.lamda_decay = lamda_decay
        self.alpha_decay_interval = alpha_decay_interval
        self.lamda_decay_interval = lamda_decay_interval
        self.start_global_steps = 0
        self.start_episode = 0

        layers = OrderedDict()
        prev = num_inputs
        for i, hidden_units in enumerate(num_hidden_units):
            layers["hidden_" + str(i)] = nn.Linear(num_inputs, hidden_units)
            layers["hidden_activation_" + str(i)] = hidden_activation
            prev = hidden_units
        layers["output"] = nn.Linear(prev, 1)
        layers["output_activation"] = nn.Sigmoid()

        self.model = nn.Sequential(layers)

    def forward(self, x):
        x = torch.from_numpy(np.array(x))
        x = self.model(x)
        return x

    def update_weights(self, p, p_next, eligibility_trace):
        """
        Update the weights according to the TD-Lambda algorithm.
        
        :param p: Float. Model's output for the current state.
        :param p_next: Float. Model's output for the next state.
        :param eligibility_trace: List of tensors. Eligibility trace for the TD-Lambda algorithm.
        """
        self.zero_grad()
        p.backward()
        with torch.no_grad():
            for i, weights in enumerate(list(self.parameters())):
                eligibility_trace[i] = self.starting_lamda * eligibility_trace[i] + weights.grad
                updated_weights = weights + self.starting_alpha * (p_next - p) * eligibility_trace[i]
                weights.copy_(updated_weights)

    def checkpoint(self, checkpoint_path, episode, global_steps, name):
        """
        Save the model's state to disk.
        
        :param checkpoint_path: String. Directory in which to save the file.
        :param episode: Integer. Number of episodes completed.
        :param global_steps: Integer. Number of global steps completed.
        :param name: String. Name of model.
        """
        formatted_date = datetime.datetime.now().strftime('%Y%m%d_%H%M_%S_%f')
        path = checkpoint_path + "/{}_{}_{}.tar".format(name, formatted_date, episode + 1)
        torch.save({'episode': episode + 1, 'global_steps': global_steps, 'model_state_dict': self.state_dict()}, path)
        print("\nCheckpoint saved: {}".format(path))

    def load(self, checkpoint_path):
        """
        Load the model's state from disk.
        
        :param checkpoint_path: String. File path of stored model.
        """
        checkpoint = torch.load(checkpoint_path)
        self.start_episode = checkpoint['episode']
        self.start_global_steps = checkpoint['global_steps']
        self.load_state_dict(checkpoint['model_state_dict'])

    def train_agent(self, num_episodes, checkpoint_path=None, checkpoint_interval=0, name=''):
        """
        
        :param num_episodes: Integer. Number of episodes to train the model for.
        :param checkpoint_path: String. Directory in which to save the model at checkpoints.
        :param checkpoint_interval: Integer. Number of episodes per checkpoint.
        :param name: Name of model.
        """
        start_episode = self.start_episode
        num_episodes += start_episode

        wins = [0, 0]
        agents = [TDAgent(0, self), TDAgent(1, self)]

        global_steps = self.start_global_steps

        for episode in range(start_episode, num_episodes):

            # Decay these parameters
            self.starting_lamda = max(self.min_lamda, self.starting_lamda * pow(self.lamda_decay,
                                                                                global_steps / self.lamda_decay_interval))
            self.starting_alpha = max(self.min_alpha, self.starting_alpha * pow(self.alpha_decay,
                                                                                global_steps / self.alpha_decay_interval))

            eligibility_trace = [torch.zeros(weights.shape, requires_grad=False) for weights
                                  in list(self.parameters())]
            game = Game(agents)
            current_player = random.randint(0, 1)
            features = game.board.get_features(current_player)

            for game_step in count():

                game.next_turn(current_player, game.roll_dice())
                current_player = not current_player
                features_next = game.board.get_features(current_player)
                p = self(features)
                p_next = self(features_next)
                if game.winner() is not None:
                    break
                features = features_next
                self.update_weights(p, p_next, eligibility_trace)

            winner = game.winner()
            wins[winner] += 1
            self.update_weights(self(features), float(winner), eligibility_trace)

            print("Episode: {}, Winner: {}, {} game steps; Wins: 0={}({}%) vs 1={}({}%)".format(
                episode + 1, winner, game_step,
                wins[0], (wins[0] / sum(wins)) * 100,
                wins[1], (wins[1] / sum(wins)) * 100))

            global_steps += game_step

            if checkpoint_path and checkpoint_interval > 0 and episode > 0 and (
                        episode + 1) % checkpoint_interval == 0:
                self.checkpoint(checkpoint_path=checkpoint_path, episode=episode, global_steps=global_steps,
                                name=name)

        if checkpoint_path:
            self.checkpoint(checkpoint_path=checkpoint_path, episode=num_episodes - 1, global_steps=global_steps,
                            name=name)
