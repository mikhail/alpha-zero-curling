import logging
from os import path

import coloredlogs
import torch

import log_handler
from Coach import Coach
from curling.game import CurlingGame
from pytorch.NNet import NNetWrapper
from utils import *

log = logging.getLogger('')
stream = logging.StreamHandler()
stream.setLevel(logging.INFO)
log.addHandler(stream)

fmt = '%(asctime)s %(filename).5s:%(lineno)s %(funcName)s [%(levelname)s] %(message)s'
coloredlogs.install(level='INFO', fmt=fmt)

torch.set_num_interop_threads(4)
torch.set_num_threads(4)

args = dotdict({
    'numIters': 200,
    'numEps': 10,  # Number of complete self-play games to simulate during a new iteration.
    'tempThreshold': 4,  # Number of moves to "explore" before choosing optimal moves
    'updateThreshold': 0.51,
    # During arena playoff, new neural net will be accepted if threshold or more of games are won.
    'maxlenOfQueue': 500,  # Number of game examples to train the neural networks.
    'numMCTSSims': 90,  # Number of games moves for MCTS to simulate.
    'arenaCompare': 8,  # Number of games to play during arena play to determine if new net will be accepted.
    'cpuct': 1,
    'parallel': 4,

    'checkpoint': './curling/data_10_layers_256/',
    'load_folder_file': ('./curling/data_10_layers_256/', 'checkpoint_best.pth.tar'),
    'numItersForTrainExamplesHistory': 100,
})

args['load_model'] = path.exists(''.join(args['load_folder_file']))


@log_handler.on_error(capacity=300)
def main():
    log.info('Cuda enabled: %s', torch.cuda.is_available())

    log.info('Loading Coach...')
    c = Coach(CurlingGame, NNetWrapper, args)

    if args.load_model:
        log.info("Load trainExamples from file")
        c.loadTrainExamples()

    log.info('Learning...')
    c.learn()


if __name__ == "__main__":
    main()
