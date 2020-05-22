"""
Provides 1 action that NNet would take given a board input.
"""
import json
import logging
import os
import time

import coloredlogs
import jsonschema
import numpy as np
import socketio

import utils
from MCTS import MCTS
from curling import constants as c
from curling import utils as c_utils
from curling.game import CurlingGame
from pytorch.NNet import NNetWrapper as NNet

log = logging.getLogger(__name__)
fmt = '%(asctime)s %(filename).5s:%(lineno)s %(funcName)s [%(levelname)s] %(message)s'
coloredlogs.install(level='INFO', logger=log)

game = CurlingGame()

log.info('Loading NNet for Curling...')
n1 = NNet(game)
log.info('Loading checkpoint...')
n1.load_checkpoint('./curling/data_image/kirill', 'checkpoint_best.pth.tar')
log.info('Ready! 🚀 ')

AZ_TEAM = int(os.environ.get('AZ_TEAM', '0'))
assert AZ_TEAM in [0, 1]
AZ_TEAM_OMO = c.P2 if AZ_TEAM == 0 else c.P1
AZ_COLOR = 'blue' if AZ_TEAM == 0 else 'red'
AZ_NAME = f"🧠 AlphaZero ({AZ_COLOR})"


def get_best_action(board, use_mcts: bool, player: AZ_TEAM_OMO):
    if use_mcts:
        now = time.time()
        args1 = utils.dotdict({'numMCTSSims': 10, 'cpuct': 2.0})
        mcts1 = MCTS(game, n1, args1)
        board = game.getCanonicalForm(board, player)
        while time.time() - now < 7:  # think for 7 seconds
            best_action = np.argmax(mcts1.getActionProb(board, temp=0))
            log.info('Considering the shot: ' + str(c_utils.decodeAction(best_action)))
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
    sio.emit('update_name', AZ_NAME)


@sio.event
def shot(data):
    log.info('Player took a shot: %s' % data)
    log.info('Waiting for board state.')


@sio.event
def state(data):
    log.info('message received with %s', data)
    jsonschema.validate(data, json.load(open('./curling/schema.json')))
    board = game.boardFromSchema(data)
    try:
        next_player = c_utils.getNextPlayer(board)
    except c_utils.NobodysTurn:
        log.warning("Game over.")
        return
    log.info('Board: %s', game.stringRepresentation(board))
    log.info('Next player: %s', next_player)
    if next_player != AZ_TEAM_OMO:
        return
    log.info('Got board. calculating action')
    sio.emit('update_name', AZ_NAME + " thinking ...")
    action = get_best_action(board, use_mcts=True, player=AZ_TEAM_OMO)
    action['color'] = AZ_COLOR
    action['handle'] *= 0.07

    log.info('responding with action: %s' % (action,))

    sio.emit('update_name', AZ_NAME)
    sio.emit('shot', action)


@sio.event
def disconnect():
    log.info('disconnected from server')


sio.connect('http://localhost:3000/?room=/curling.gg/vs_ai')
# sio.connect('http://curling-socket.herokuapp.com/?room=/vs-ai')
sio.wait()
