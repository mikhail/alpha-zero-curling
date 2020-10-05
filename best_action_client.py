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

import log_handler
import utils
from MCTS import MCTS
from curling import constants as c
from curling import utils as c_utils
from curling.game import CurlingGame
from pytorch.NNet import NNetWrapper as NNet

log = logging.getLogger('')
fmt = '%(asctime)s %(filename).5s:%(lineno)s %(funcName)s [%(levelname)s] %(message)s'
coloredlogs.install(level='INFO', logger=log)
root = logging.getLogger('root')
root.setLevel('INFO')

logging.getLogger('engineio').setLevel('WARN')
logging.getLogger('socketio').setLevel('WARN')

game = CurlingGame()

log.info('Loading NNet for Curling...')
nnet = NNet(game)
log.info('Loading checkpoint...')
nnet.load_checkpoint('./kirill/ann_6_features/', 'checkpoint_best.pth.tar')
log.info('Ready! 🚀 ')

AZ_TEAM = int(os.environ.get('AZ_TEAM', '0'))
assert AZ_TEAM in [0, 1]
AZ_TEAM_OMO = c.P2 if AZ_TEAM == 0 else c.P1
AZ_COLOR = 'blue' if AZ_TEAM == 0 else 'red'
AZ_NAME = f"🧠 AlphaZero ({AZ_COLOR})"


@log_handler.on_error()
def get_best_action_web(board, use_mcts: bool, player: AZ_TEAM_OMO):
    best_action = get_best_action(board, player, use_mcts)
    log.info('Choosing the shot: ' + str(c_utils.decodeAction(best_action)))
    handle, weight, broom = c_utils.decodeAction(best_action)

    next_state, next_player = game.getNextState(board, 1, int(best_action))
    next_state = game.getCanonicalForm(next_state, next_player)

    action_obj = {"handle": handle, "weight": str(weight).title(), "broom": broom}
    return action_obj, next_state


def get_best_action(board, player, use_mcts):
    if use_mcts:
        args1 = utils.dotdict({'numMCTSSims': 128, 'cpuct': 1.0})
        mcts1 = MCTS(game, nnet, args1)
        board = game.getCanonicalForm(board, player)
        best_action = int(np.argmax(mcts1.getActionProb(board, temp=0)))
    else:
        p, v = nnet.predict(board)
        best_action = int(np.argmax(p))
    return best_action


sio = socketio.Client(logger=False)


@sio.event
def connect():
    log.info('connection established')
    sio.emit('set_username', AZ_NAME)
    sio.emit('get_history')


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
        next_player = c_utils.getNextPlayer(board, c.P1)
    except c_utils.NobodysTurn:
        log.warning("Game over.")
        return
    log.info('Board: %s', game.stringRepresentation(board))
    log.info('Next player: %s', next_player)
    if next_player != AZ_TEAM_OMO:
        return
    log.info('Got board. calculating action')
    sio.emit('set_username', AZ_NAME + " thinking ...")
    action, state = get_best_action_web(board, use_mcts=True, player=AZ_TEAM_OMO)
    action['color'] = AZ_COLOR
    action['handle'] *= 0.07

    log.info('responding with action: %s' % (action,))

    sio.emit('set_username', AZ_NAME)
    sio.emit('shot', action)
    time.sleep(5)
    state = game.getCanonicalForm(state, 0 - AZ_TEAM_OMO)
    sio.emit('set_state', game.boardToSchema(state))

@sio.event
def disconnect():
    log.info('disconnected from server')


if __name__ == '__main__':
    sio.connect('http://localhost:3000/?room=/vs_ai')
    # sio.connect('http://curling-socket.herokuapp.com/?room=/vs-ai')
    sio.wait()
