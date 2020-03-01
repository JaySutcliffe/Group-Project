import os
from agents import TDAgent, RandomAgent, PubevalAgent
from evaluator import EvaluationModel
from game import Game
from torch import nn


def train(name='',
          num_episodes=100000,
          checkpoint_path='', checkpoint_interval=1000,
          hidden_layers=(40,),
          starting_alpha=0.1, starting_lamda=0.9,
          min_alpha=0.1, min_lamda=0.7,
          alpha_decay=1, lamda_decay=0.96,
          alpha_decay_interval=1, lamda_decay_interval=3e4,
          hidden_activation=nn.Sigmoid(), num_inputs=198,
          existing_model_path=''):
    model = EvaluationModel(hidden_layers=hidden_layers,
                            starting_alpha=starting_alpha, starting_lamda=starting_lamda,
                            min_alpha=min_alpha, min_lamda=min_lamda,
                            alpha_decay=alpha_decay, lamda_decay=lamda_decay,
                            alpha_decay_interval=alpha_decay_interval, lamda_decay_interval=lamda_decay_interval,
                            hidden_activation=hidden_activation, num_inputs=num_inputs)

    if existing_model_path:
        model.load(checkpoint_path=existing_model_path)

    model.train_agent(num_episodes=num_episodes, checkpoint_save_path=checkpoint_path,
                      checkpoint_interval=checkpoint_interval, name=name)


def evaluate(existing_model_path,
             num_episodes=100000,
             hidden_layers=(40,),
             starting_alpha=0.1, starting_lamda=0.9,
             min_alpha=0.1, min_lamda=0.7,
             alpha_decay=1, lamda_decay=0.96,
             alpha_decay_interval=1, lamda_decay_interval=3e4,
             hidden_activation=nn.Sigmoid(), num_inputs=198,
             opponent="pubeval"):

    model = EvaluationModel(hidden_layers=hidden_layers,
                            starting_alpha=starting_alpha, starting_lamda=starting_lamda,
                            min_alpha=min_alpha, min_lamda=min_lamda,
                            alpha_decay=alpha_decay, lamda_decay=lamda_decay,
                            alpha_decay_interval=alpha_decay_interval, lamda_decay_interval=lamda_decay_interval,
                            hidden_activation=hidden_activation, num_inputs=num_inputs)

    model.load(checkpoint_path=existing_model_path)

    if opponent == "pubeval":
        opponent_agent = PubevalAgent(0)
    else:
        opponent_agent = RandomAgent(0)
    agents = [opponent_agent, TDAgent(1, model)]
    wins = [0, 0]
    for i in range(num_episodes):
        game = Game(agents)
        wins[game.play()[0]] += 1

    print("\n{}: \t{}".format(existing_model_path, float(wins[1]) / float(sum(wins))))


def evaluate_dir(dir_path,
                 num_episodes=100000,
                 hidden_layers=(40,),
                 starting_alpha=0.1, starting_lamda=0.9,
                 min_alpha=0.1, min_lamda=0.7,
                 alpha_decay=1, lamda_decay=0.96,
                 alpha_decay_interval=1, lamda_decay_interval=3e4,
                 hidden_activation=nn.Sigmoid(), num_inputs=198,
                 opponent="pubeval"):

    for root, dirs, files in os.walk(dir_path):
        for file in sorted(files):
            if ".tar" in file:
                evaluate(os.path.join(root, file),
                         num_episodes=num_episodes,
                         hidden_layers=hidden_layers,
                         starting_alpha=starting_alpha, starting_lamda=starting_lamda,
                         min_alpha=min_alpha, min_lamda=min_lamda,
                         alpha_decay=alpha_decay, lamda_decay=lamda_decay,
                         alpha_decay_interval=alpha_decay_interval, lamda_decay_interval=lamda_decay_interval,
                         hidden_activation=hidden_activation, num_inputs=num_inputs,
                         opponent=opponent)
