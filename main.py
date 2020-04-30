import logging
from os import path

import coloredlogs
import torch

from Coach import Coach
from curling.game import CurlingGame
from pytorch.NNet import NNetWrapper as nn
from utils import *
import log_handler

log = logging.getLogger('')
stream = logging.StreamHandler()
stream.setLevel(logging.INFO)
log.addHandler(stream)

fmt = '%(asctime)s %(filename)s:%(lineno)s %(funcName)s [%(levelname)s] %(message)s'
coloredlogs.install(level='INFO', fmt=fmt)

torch.set_num_interop_threads(12)
torch.set_num_threads(12)

args = dotdict({
    'numIters': 10,
    'numEps': 10,  # Number of complete self-play games to simulate during a new iteration.
    'tempThreshold': 4,  # Number of moves to "explore" before choosing optimal moves
    'updateThreshold': 0.51,
    # During arena playoff, new neural net will be accepted if threshold or more of games are won.
    'maxlenOfQueue': 1000,  # Number of game examples to train the neural networks.
    'numMCTSSims': 45,  # Number of games moves for MCTS to simulate.
    'arenaCompare': 4,  # Number of games to play during arena play to determine if new net will be accepted.
    'cpuct': 2,

    'checkpoint': './curling/data_image/',
    'load_model': True,
    'load_folder_file': ('./curling/data_image/', 'checkpoint_best.pth.tar'),
    'numItersForTrainExamplesHistory': 10000,

})

args['load_model'] = path.exists(''.join(args['load_folder_file']))


@log_handler.on_error()
def main():
    log.info('Cuda enabled: %s', torch.cuda.is_available())
    log.info('Loading Curling...')
    g = CurlingGame()

    log.info('Loading nn...')
    nnet = nn(g)

    if args.load_model:
        log.info('Loading checkpoint...')
        nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])

    log.info('Loading Coach...')
    c = Coach(g, nnet, args)

    if args.load_model:
        log.info("Load trainExamples from file")
        c.loadTrainExamples()

    log.info('Learning...')
    c.learn()


if __name__ == "__main__":
    main()
