import datetime
import random
from itertools import count
import numpy as np
import torch
import torch.nn as nn
from collections import OrderedDict
from agents import TDAgent
from game import Game

torch.set_default_tensor_type('torch.DoubleTensor')

class EvaluationModel(nn.Module):

    def __init__(self, hidden_layers,
                 starting_alpha, starting_lamda,
                 min_alpha, min_lamda,
                 alpha_decay, lamda_decay,
                 alpha_decay_interval, lamda_decay_interval,
                 hidden_activation=nn.Sigmoid(), num_inputs=198):

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
        for i, hidden_units in enumerate(hidden_layers):
            self.layers["hidden_"+str(i)] = nn.Linear(num_inputs, hidden_units)
            self.layers["hidden_activation_"+str(i)] = hidden_activation
            prev = hidden_units
        self.layers["output"] = nn.Linear(prev, 1)
        self.layers["output_activation"] = nn.Sigmoid()

        self.model = nn.Sequential(layers)

    def forward(self, x):
        x = torch.from_numpy(np.array(x))
        x = self.model(x)
        return x

    def update_weights(self, p, p_next, eligibility_trace):
        self.zero_grad()
        p.backward()
        with torch.no_grad():
            for i, weights in enumerate(list(self.parameters())):
                eligibility_trace[i] = self.starting_lamda * eligibility_trace[i] + weights.grad
                updated_weights = weights + self.starting_alpha * (p_next - p) * eligibility_trace[i]
                weights.copy_(updated_weights)

    def checkpoint(self, checkpoint_path, episode, global_steps, name):
        formatted_date = datetime.datetime.now().strftime('%Y%m%d_%H%M_%S_%f')
        path = checkpoint_path + "/{}_{}_{}.tar".format(name, formatted_date, episode+1)
        torch.save({'episode': episode + 1, 'global_steps': global_steps, 'state_dict': self.state_dict()}, path)
        print("\nCheckpoint saved: {}".format(path))

    def load(self, checkpoint_path):
        checkpoint = torch.load(checkpoint_path)
        self.start_episode = checkpoint['episode']
        self.start_global_steps = checkpoint['global_steps']
        self.load_state_dict(checkpoint['state_dict'])

    def train_agent(self, num_episodes, checkpoint_save_path=None, checkpoint_interval=0, name=''):
        start_episode = self.start_episode
        num_episodes += start_episode

        wins = [0, 0]
        agents = [TDAgent(0, self), TDAgent(1, self)]

        global_steps = self.start_global_steps

        for episode in range(start_episode, num_episodes):
            self.starting_lamda = max(self.min_lamda, self.starting_lamda * pow(self.lamda_decay, global_steps / self.lamda_decay_interval))
            self.starting_alpha = max(self.min_alpha, self.starting_alpha * pow(self.alpha_decay, global_steps / self.alpha_decay_interval))

            eligibility_traces = [torch.zeros(weights.shape, requires_grad=False) for weights
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
                if game.winner():
                    break
                features = features_next
                self.update_weights(p, p_next, eligibility_traces)

            winner = game.winner()[0]

            self.update_weights(self(features), float(winner), eligibility_traces)

            wins[winner] += 1

            print("Episode: {}, Winner: {}, {} game steps; Wins: 0={}({}%) vs 1={}({}%)".format(
                    episode + 1, winner, game_step,
                    wins[0], (wins[0] / sum(wins)) * 100,
                    wins[1], (wins[1] / sum(wins)) * 100))

            global_steps += game_step

            if checkpoint_save_path and checkpoint_interval > 0 and episode > 0 and (episode + 1) % checkpoint_interval == 0:
                self.checkpoint(checkpoint_path=checkpoint_save_path, episode=episode, global_steps=global_steps, name=name)

        if checkpoint_save_path:
            self.checkpoint(checkpoint_path=checkpoint_save_path, episode=num_episodes-1, global_steps=global_steps, name=name)