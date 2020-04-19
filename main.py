import torch

from Coach import Coach
from curling.game import CurlingGame
from pytorch.NNet import NNetWrapper as nn
# from tfwrap.NNet import NNetWrapper as nn
from utils import *

torch.set_num_interop_threads(12)
torch.set_num_threads(12)

args = dotdict({
    'numIters': 10,
    'numEps': 4,              # Number of complete self-play games to simulate during a new iteration.
    'tempThreshold': 4,        # Number of moves to "explore" before choosing optimal moves
    'updateThreshold': 0.51,     # During arena playoff, new neural net will be accepted if threshold or more of games are won.
    'maxlenOfQueue': 1000,    # Number of game examples to train the neural networks.
    'numMCTSSims': 5,          # Number of games moves for MCTS to simulate.
    'arenaCompare': 1,         # Number of games to play during arena play to determine if new net will be accepted.
    'cpuct': 2,

    'checkpoint': './curling/data_image/',
    'load_model': False,
    'load_folder_file': ('./curling/data_image/','checkpoint_best.pth.tar'),
    'numItersForTrainExamplesHistory': 10000,

})

if __name__ == "__main__":
    print('Loading Curling...')
    g = CurlingGame()
    print('Loading nn...')
    nnet = nn(g)

    if args.load_model:
        print('Loading checkpoint...')
        nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])
    print('Loading Coach...')
    c = Coach(g, nnet, args)
    if args.load_model:
        print("Load trainExamples from file")
        c.loadTrainExamples()
    print('Learning...')
    c.learn()
