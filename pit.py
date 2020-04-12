import Arena
from MCTS import MCTS
from pytorch.NNet import NNetWrapper as NNet


import numpy as np
from curling.game import CurlingGame
from curling.players import HumanPlayer

"""
use this script to play any two agents against each other, or play manually with
any agent.
"""

class dotdict(dict):
    # allow obj.attr access for dictionary params
    def __getattr__(self, name):
        return self[name]

game = CurlingGame()


hp = HumanPlayer(game).play

# nnet players
n1 = NNet(game)
n1.load_checkpoint('./curling/data_5rr/', 'checkpoint_best.pth.tar')

args1 = dotdict({'numMCTSSims': 6, 'cpuct':1.0})
mcts1 = MCTS(game, n1, args1)
n1p = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))


player1 = hp
player2 = n1p

arena = Arena.Arena(player1, player2, game, display=CurlingGame.display)

print(arena.playGames(2, verbose=True))
