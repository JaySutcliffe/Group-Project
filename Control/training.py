import os

from agents import TDAgent, RandomAgent, PubevalAgent
from evaluator import EvaluationModel
from game import Game
from torch import nn


def train(name='',
          num_episodes=100000,
          checkpoint_path='', checkpoint_interval=1000,
          num_hidden_units=(40,),
          starting_alpha=0.1, starting_lamda=0.9,
          min_alpha=0.1, min_lamda=0.7,
          alpha_decay=1, lamda_decay=0.96,
          alpha_decay_interval=1, lamda_decay_interval=3e4,
          hidden_activation=nn.Sigmoid(), num_inputs=198,
          existing_model_path=''):
    """
    Evaluates all models in the directory against an opponent and prints out the model's win rate.

    
    :param name: String. Name of the model.
    :param num_episodes: Integer. Number of games to play per model.
    :param checkpoint_path: String. Directory in which to save the model at checkpoints.
    :param checkpoint_interval: Integer. Number of episodes per checkpoint.
    :param num_hidden_units: See EvaluationModel class. 
    :param starting_alpha: See EvaluationModel class.
    :param starting_lamda: See EvaluationModel class.
    :param min_alpha: See EvaluationModel class.
    :param min_lamda: See EvaluationModel class.
    :param alpha_decay: See EvaluationModel class.
    :param lamda_decay: See EvaluationModel class.
    :param alpha_decay_interval: See EvaluationModel class.
    :param lamda_decay_interval: See EvaluationModel class.
    :param hidden_activation: See EvaluationModel class.
    :param num_inputs: See EvaluationModel class.
    :param existing_model_path: 
    """
    model = EvaluationModel(num_inputs=num_inputs, num_hidden_units=num_hidden_units,
                            starting_alpha=starting_alpha, starting_lamda=starting_lamda,
                            min_alpha=min_alpha, min_lamda=min_lamda,
                            alpha_decay=alpha_decay, lamda_decay=lamda_decay,
                            alpha_decay_interval=alpha_decay_interval, lamda_decay_interval=lamda_decay_interval,
                            hidden_activation=hidden_activation)

    if existing_model_path:
        model.load(checkpoint_path=existing_model_path)

    model.train_agent(num_episodes=num_episodes, checkpoint_path=checkpoint_path,
                      checkpoint_interval=checkpoint_interval, name=name)


def evaluate(existing_model_path,
             num_episodes=100,
             num_hidden_units=(40,),
             starting_alpha=0.1, starting_lamda=0.9,
             min_alpha=0.1, min_lamda=0.7,
             alpha_decay=1, lamda_decay=0.96,
             alpha_decay_interval=1, lamda_decay_interval=3e4,
             hidden_activation=nn.Sigmoid(), num_inputs=198,
             opponent="pubeval"):
    """
    Evaluate a saved model against an opponent and prints out the model's win rate.

    :param existing_model_path: String. Path of the saved model.
    :param num_episodes: Integer. Number of games to play per model.
    :param num_hidden_units: See EvaluationModel class. 
    :param starting_alpha: See EvaluationModel class.
    :param starting_lamda: See EvaluationModel class.
    :param min_alpha: See EvaluationModel class.
    :param min_lamda: See EvaluationModel class.
    :param alpha_decay: See EvaluationModel class.
    :param lamda_decay: See EvaluationModel class.
    :param alpha_decay_interval: See EvaluationModel class.
    :param lamda_decay_interval: See EvaluationModel class.
    :param hidden_activation: See EvaluationModel class.
    :param num_inputs: See EvaluationModel class.
    :param opponent: "pubeval" or "random".
    """

    model = EvaluationModel(num_inputs=num_inputs, num_hidden_units=num_hidden_units,
                            starting_alpha=starting_alpha, starting_lamda=starting_lamda,
                            min_alpha=min_alpha, min_lamda=min_lamda,
                            alpha_decay=alpha_decay, lamda_decay=lamda_decay,
                            alpha_decay_interval=alpha_decay_interval, lamda_decay_interval=lamda_decay_interval,
                            hidden_activation=hidden_activation)

    model.load(checkpoint_path=existing_model_path)

    if opponent == "pubeval":
        opponent_agent = PubevalAgent(0)
    else:
        opponent_agent = RandomAgent(0)
    agents = [opponent_agent, TDAgent(1, model)]
    wins = [0, 0]
    for i in range(num_episodes):
        game = Game(agents)
        wins[game.play()] += 1

    print("\n{}: \t{}".format(existing_model_path, float(wins[1]) / float(sum(wins))))


def evaluate_dir(dir_path,
                 num_episodes=100,
                 num_hidden_units=(40,),
                 starting_alpha=0.1, starting_lamda=0.9,
                 min_alpha=0.1, min_lamda=0.7,
                 alpha_decay=1, lamda_decay=0.96,
                 alpha_decay_interval=1, lamda_decay_interval=3e4,
                 hidden_activation=nn.Sigmoid(), num_inputs=198,
                 opponent="pubeval"):
    """
    Evaluates all models in the directory against an opponent and prints out the models' win rate.
    
    :param dir_path: String. Path to the directory containing the saved models.
    :param num_episodes: Integer. Number of games to play per model.
    :param num_hidden_units: See EvaluationModel class. 
    :param starting_alpha: See EvaluationModel class.
    :param starting_lamda: See EvaluationModel class.
    :param min_alpha: See EvaluationModel class.
    :param min_lamda: See EvaluationModel class.
    :param alpha_decay: See EvaluationModel class.
    :param lamda_decay: See EvaluationModel class.
    :param alpha_decay_interval: See EvaluationModel class.
    :param lamda_decay_interval: See EvaluationModel class.
    :param hidden_activation: See EvaluationModel class.
    :param num_inputs: See EvaluationModel class.
    :param opponent: "pubeval" or "random".
    """

    for root, dirs, files in os.walk(dir_path):
        for file in sorted(files):
            if ".tar" in file:
                evaluate(os.path.join(root, file),
                         num_episodes=num_episodes,
                         num_inputs=num_inputs, num_hidden_units=num_hidden_units,
                         starting_alpha=starting_alpha, starting_lamda=starting_lamda,
                         min_alpha=min_alpha, min_lamda=min_lamda,
                         alpha_decay=alpha_decay, lamda_decay=lamda_decay,
                         alpha_decay_interval=alpha_decay_interval, lamda_decay_interval=lamda_decay_interval,
                         hidden_activation=hidden_activation,
                         opponent=opponent)

if __name__ == "__main__":
    evaluate_dir("./stored_models/final", num_episodes=1000)
