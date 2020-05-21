"""
Provides 1 action that NNet would take given a board input.
"""
import json
import logging

import coloredlogs
import jsonschema
import numpy as np
import socketio

import log_handler
import utils
from MCTS import MCTS
from curling import utils as c_utils
from curling.game import CurlingGame
from curling import constants as c
from pytorch.NNet import NNetWrapper as NNet

log = logging.getLogger(__name__)
stream = logging.StreamHandler()
stream.setLevel(logging.INFO)
log.addHandler(stream)

fmt = '%(asctime)s %(filename).5s:%(lineno)s %(funcName)s [%(levelname)s] %(message)s'
coloredlogs.install(level='INFO', fmt=fmt, logger=log)

game = CurlingGame()

log.info('Loading NNet for Curling...')
n1 = NNet(game)
log.info('Loading checkpoint...')
n1.load_checkpoint('./curling/data_image/kirill', 'checkpoint_best.pth.tar')
log.info('Ready! 🚀 ')


def get_best_action(board, use_mcts=False, player=1):
    if use_mcts:
        args1 = utils.dotdict({'numMCTSSims': 100, 'cpuct': 1.0})
        mcts1 = MCTS(game, n1, args1)
        board = game.getCanonicalForm(board, player)
        best_action = np.argmax(mcts1.getActionProb(board, temp=0))
    else:
        p, v = n1.predict(board)
        best_action = np.argmax(p)
    handle, weight, broom = c_utils.decodeAction(best_action)
    return {
        "handle": handle,
        "weight": str(weight).title(),
        "broom": broom
    }


sio = socketio.Client(logger=False)


@sio.event
def connect():
    log.info('connection established')
    sio.emit('update_name', "🧠 AlphaZero")


@sio.event
def shot(data):
    log.info('Player took a shot: %s' % data)
    log.info('Waiting for board state.')


@sio.event
def state(data):
    log.info('message received with %s', data)
    jsonschema.validate(data, json.load(open('./curling/schema.json')))
    board = game.boardFromSchema(data)
    next_player = c_utils.getNextPlayer(board)
    log.info('Board: %s', game.stringRepresentation(board))
    log.info('Next player: %s', next_player)
    if next_player != c.P2:
        return
    log.info('Got board. calculating action')
    action = get_best_action(board, use_mcts=True, player=-1)
    action['color'] = 'blue'
    action['handle'] = -0.07

    log.info('responding with action: %s' % (action,))

    sio.emit('shot', action)


@sio.event
def disconnect():
    log.info('disconnected from server')


sio.connect('http://localhost:3000/?room=/curling.gg/vs_ai')
sio.wait()
