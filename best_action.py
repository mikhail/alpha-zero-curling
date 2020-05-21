"""
Provides 1 action that NNet would take given a board input.
"""
import argparse
import json

import numpy as np

import utils
from MCTS import MCTS
from curling.game import CurlingGame
from curling.utils import decodeAction
from pytorch.NNet import NNetWrapper as NNet

parser = argparse.ArgumentParser()
parser.add_argument('--board', '-b', type=str, help='String representation of a board', required=True)

args = parser.parse_args()

game = CurlingGame()

n1 = NNet(game)
n1.load_checkpoint('./curling/data_image/', 'checkpoint_best.pth.tar')

board = game.boardFromString(args.board)
use_mcts = False

if use_mcts:
    args1 = utils.dotdict({'numMCTSSims': 2, 'cpuct': 1.0})
    mcts1 = MCTS(game, n1, args1)
    best_action = np.argmax(mcts1.getActionProb(board, temp=0))
else:
    p, v = n1.predict(board)
    best_action = np.argmax(p)

handle, weight, broom = decodeAction(best_action)
print(json.dumps({
    "handle": handle,
    "weight": weight,
    "broom": broom
}))
