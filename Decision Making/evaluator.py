import datetime
import random
import time
from itertools import count

import numpy as np
import torch
import torch.nn as nn

from agents import TDAgent
from game import Game

torch.set_default_tensor_type('torch.DoubleTensor')


class EvaluationModel(nn.Module):

    def __init__(self, hidden_units, alpha, lamda, seed=0, input_units=198, output_units=1):
        super(EvaluationModel, self).__init__()
        self.alpha = alpha
        self.lamda = lamda

        self.start_episode = 0

        torch.manual_seed(seed)
        random.seed(seed)

        self.hidden = nn.Sequential(nn.Linear(input_units, hidden_units), nn.Sigmoid())
        self.output = nn.Sequential(nn.Linear(hidden_units, output_units), nn.Sigmoid())

    def forward(self, x):
        x = torch.from_numpy(np.array(x))
        x = self.hidden(x)
        x = self.output(x)
        return x

    def update_weights(self, p, p_next, eligibility_traces):
        self.zero_grad()
        p.backward()

        with torch.no_grad():

            delta = p_next - p
            parameters = list(self.parameters())

            for i, weights in enumerate(parameters):
                eligibility_traces[i] = self.lamda * eligibility_traces[i] + weights.grad
                new_weights = weights + self.alpha * delta * eligibility_traces[i]
                weights.copy_(new_weights)

        return delta

    def checkpoint(self, checkpoint_path, step, name_experiment):
        path = checkpoint_path + "/{}_{}_{}.tar".format(name_experiment, datetime.datetime.now().strftime('%Y%m%d_%H%M_%S_%f'), step + 1)
        torch.save({'step': step + 1, 'model_state_dict': self.state_dict()}, path)
        print("\nCheckpoint saved: {}".format(path))

    def load(self, checkpoint_path):
        checkpoint = torch.load(checkpoint_path)
        self.start_episode = checkpoint['step']
        self.load_state_dict(checkpoint['model_state_dict'])

    def train_agent(self, n_episodes, save_path=None, save_step=0, name_experiment=''):
        start_episode = self.start_episode
        n_episodes += start_episode

        wins = [0, 0]
        agents = [TDAgent(0, self), TDAgent(1, self)]

        durations = []
        total_game_steps = 0
        start_training = time.time()

        for episode in range(start_episode, n_episodes):
            if episode % 30000 == 0:
                self.lamda = max(0.7, 0.9*pow(0.96, episode/30000))

            if episode % 40000 == 0:
                self.alpha = max(0.01, 0.1*pow(0.96, episode/40000))


            eligibility_traces = [torch.zeros(weights.shape, requires_grad=False) for weights
                                  in list(self.parameters())]
            game = Game(agents)
            current_player = random.randint(0, 1)
            observation = game.get_features(current_player)
            t = time.time()

            for game_step in count():

                game.next_turn(current_player, game.roll_dice())
                current_player = not current_player
                observation_next = game.get_features(current_player)
                p = self(observation)
                p_next = self(observation_next)
                if game.winner():
                    break
                observation = observation_next
                self.update_weights(p, p_next, eligibility_traces)

            winner = game.winner()[0]

            self.update_weights(self(observation), winner, eligibility_traces)

            wins[winner] += 1
            tot = sum(wins)

            print(
                "Game={:<6d} | Winner={} | after {:<4} plays || Wins: 0={:<6}({:<5.1f}%) | 1={:<6}({:<5.1f}%) | Duration={:<.3f} sec".format(
                    episode + 1, winner, game_step,
                    wins[0], (wins[0] / tot) * 100,
                    wins[1], (wins[1] / tot) * 100,
                    time.time() - t))

            durations.append(time.time() - t)
            total_game_steps += game_step

            if save_path and save_step > 0 and episode > 0 and (episode + 1) % save_step == 0:
                self.checkpoint(checkpoint_path=save_path, step=episode, name_experiment=name_experiment)

        print("\nAverage duration per game: {} seconds".format(round(sum(durations) / n_episodes, 3)))
        print("Average game length: {} plays | Total Duration: {}".format(round(total_game_steps / n_episodes, 2), datetime.timedelta(seconds=int(time.time() - start_training))))

        if save_path:
            self.checkpoint(checkpoint_path=save_path, step=n_episodes - 1, name_experiment=name_experiment)

            with open('{}/comments.txt'.format(save_path), 'a') as file:
                file.write("Average duration per game: {} seconds".format(round(sum(durations) / n_episodes, 3)))
                file.write("\nAverage game length: {} plays | Total Duration: {}".format(round(total_game_steps / n_episodes, 2), datetime.timedelta(seconds=int(time.time() - start_training))))
