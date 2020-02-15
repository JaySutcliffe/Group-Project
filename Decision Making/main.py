import argparse
import utils


def formatter(prog):
    return argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=100, width=180)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TD-Gammon', formatter_class=lambda prog: formatter(prog))
    subparsers = parser.add_subparsers(help='Train TD-Network | Evaluate Agent(s) | Plot Wins')

    parser_train = subparsers.add_parser('train', help='Train TD-Network', formatter_class=lambda prog: formatter(prog))
    parser_train.add_argument('--save_path', help='Save directory location', type=str, default=None)
    parser_train.add_argument('--save_step', help='Save the model every n episodes/games', type=int, default=0)
    parser_train.add_argument('--episodes', help='Number of episodes/games', type=int, default=200000)
    parser_train.add_argument('--alpha', help='Learning rate', type=float, default=0.1)
    parser_train.add_argument('--hidden_units', help='Hidden units', type=int, default=50)
    parser_train.add_argument('--lamda', help='Credit assignment parameter', type=float, default=0.9)
    parser_train.add_argument('--model', help='Directory location to the model to be restored', type=str, default=None)
    parser_train.add_argument('--name', help='Name of the experiment', type=str, default='exp1')
    parser_train.add_argument('--seed', help='Seed used to reproduce results', type=int, default=0)

    parser_train.set_defaults(func=utils.args_train)

    parser_evaluate = subparsers.add_parser('evaluate', help='Evaluate Agent(s)', formatter_class=lambda prog: formatter(prog))
    parser_evaluate.add_argument('--model_agent0', help='Saved model used by the agent0 (WHITE)', required=True, type=str)
    parser_evaluate.add_argument('--model_agent1', help='Saved model used by the agent1 (BLACK)', required=False, type=str)
    parser_evaluate.add_argument('--hidden_units_agent0', help='Hidden Units of the model used by the agent0 (WHITE)', required=False, type=int, default=40)
    parser_evaluate.add_argument('--hidden_units_agent1', help='Hidden Units of the model used by the agent1 (BLACK)', required=False, type=int, default=40)
    parser_evaluate.add_argument('--episodes', help='Number of episodes/games', default=20, required=False, type=int)

    parser_evaluate.set_defaults(func=utils.args_evaluate)

    parser_plot = subparsers.add_parser('plot', help='Plot the performance (wins)', formatter_class=lambda prog: formatter(prog))
    parser_plot.add_argument('--save_path', help='Directory where the model are saved', type=str, required=True)
    parser_plot.add_argument('--hidden_units', help='Hidden units of the model(s) loaded', type=int, default=50)
    parser_plot.add_argument('--episodes', help='Number of episodes/games against a single opponent', default=20, type=int)
    parser_plot.add_argument('--opponent', help='Opponent(s) agent(s) (delimited by comma) - "random" and/or "gnubg"', default='random', type=str)
    parser_plot.add_argument('--dst', help='Save directory location', type=str, default='myexp')

    parser_plot.set_defaults(func=utils.args_plot)

    args = parser.parse_args()
    args.func(args)
