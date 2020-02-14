import os
import sys
from agents import TDAgent, RandomAgent
from evaluator import EvaluationModel
from torch.utils.tensorboard import SummaryWriter
from game import Game


def write_file(path, **kwargs):
    with open('{}/parameters.txt'.format(path), 'w+') as file:
        print("Parameters:")
        for key, value in kwargs.items():
            file.write("{}={}\n".format(key, value))
            print("{}={}".format(key, value))
        print()


def path_exists(path):
    if os.path.exists(path):
        return True
    else:
        print("The path {} doesn't exists".format(path))
        sys.exit()


def args_train(args):
    save_step = args.save_step
    save_path = None
    n_episodes = args.episodes
    alpha = args.alpha
    hidden_units = args.hidden_units
    lamda = args.lamda
    name = args.name
    seed = args.seed

    net = EvaluationModel(hidden_units=hidden_units, alpha=alpha, lamda=lamda, seed=seed)

    if args.model and path_exists(args.model):
        net.load(checkpoint_path=args.model)

    if args.save_path and path_exists(args.save_path):
        save_path = args.save_path

        write_file(
            save_path, save_path=args.save_path, command_line_args=args, hidden_units=hidden_units,
            init_weights=init_weights, alpha=net.alpha, lamda=net.lamda,
            n_episodes=n_episodes, save_step=save_step, start_episode=net.start_episode, name_experiment=name,
            restored_model=args.model, seed=seed,
            modules=[module for module in net.modules()]
        )

    net.train_agent(n_episodes=n_episodes, save_path=save_path, save_step=save_step, name_experiment=name)


def args_evaluate(args):
    model_agent0 = args.model_agent0
    model_agent1 = args.model_agent1
    hidden_units_agent0 = args.hidden_units_agent0
    hidden_units_agent1 = args.hidden_units_agent1
    n_episodes = args.episodes

    if path_exists(model_agent0) and path_exists(model_agent1):

        net0 = EvaluationModel(hidden_units=hidden_units_agent0, alpha=0.1, lamda=None)
        net1 = EvaluationModel(hidden_units=hidden_units_agent1, alpha=0.1, lamda=None)

        net0.load(checkpoint_path=model_agent0)
        net1.load(checkpoint_path=model_agent1)

        agents = [TDAgent(0, net1), TDAgent(1, net1)]
        wins = [0, 0]
        for i in range(n_episodes):
            game = Game(agents)
            wins[game.play()[0]] += 1

        print(wins)


def args_plot(args):
    src = args.save_path
    hidden_units = args.hidden_units
    n_episodes = args.episodes
    opponents = args.opponent.split(',')

    if path_exists(src):

        dst = args.dst

        for root, dirs, files in os.walk(src):
            global_step = 0
            files = sorted(files)

            writer = SummaryWriter(dst)

            for file in files:
                if ".tar" in file:
                    print("\nLoad {}".format(os.path.join(root, file)))

                    net = EvaluationModel(hidden_units=hidden_units, alpha=0.1, lamda=None)

                    net.load(checkpoint_path=os.path.join(root, file))

                    if 'random' in opponents:
                        tag_scalar_dict = {}
                        agents = [TDAgent(1, net), RandomAgent()]
                        wins = [0, 0]
                        for i in range(n_episodes):
                            game = Game(agents)
                            wins[game.play()[0]] += 1
                        tag_scalar_dict['random'] = wins[0]

                        writer.add_scalars('wins_vs_random/', tag_scalar_dict, global_step)

                    global_step += 1

                    writer.close()
