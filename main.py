#!/usr/bin/env python

from Coach import Coach
from curling.game import CurlingGame
from othello.pytorch.NNet import NNetWrapper as nn
from utils import *

args = dotdict({
    'numIters': 10,
    'numEps': 2,              # Number of complete self-play games to simulate during a new iteration.
    'tempThreshold': 1,        # Number of moves to "explore" before choosing optimal moves
    'updateThreshold': 0.5,     # During arena playoff, new neural net will be accepted if threshold or more of games are won.
    'maxlenOfQueue': 10,    # Number of game examples to train the neural networks.
    'numMCTSSims': 40,          # Number of games moves for MCTS to simulate.
    'arenaCompare': 4,         # Number of games to play during arena play to determine if new net will be accepted.
    'cpuct': 2,

    'checkpoint': './temp/',
    'load_model': True,
    'load_folder_file': ('./temp/','checkpoint_7.pth.tar'),
    'numItersForTrainExamplesHistory': 1000,

})

if __name__ == "__main__":
    g = CurlingGame()
    nnet = nn(g)

    if args.load_model:
        nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])

    c = Coach(g, nnet, args)
    if args.load_model:
        print("Load trainExamples from file")
        c.loadTrainExamples()
    c.learn()
