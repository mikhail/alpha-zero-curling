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

human_vs_cpu = True

g = CurlingGame()

print(g.getBoardSize())

hp = HumanPlayer(g).play

# nnet players
n1 = NNet(g)
#n1.load_checkpoint('./temp/', 'best.pth.tar')
n1.load_checkpoint('./temp/', 'checkpoint_5.pth.tar')

args1 = dotdict({'numMCTSSims': 50, 'cpuct':1.0})
mcts1 = MCTS(g, n1, args1)
n1p = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))

arena = Arena.Arena(n1p, hp, g, display=CurlingGame.display)

print(arena.playGames(2, verbose=True))
