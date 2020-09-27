import logging
import os
import random
import sys
import time
from datetime import datetime
from pickle import Pickler, Unpickler

import numpy as np
import torch.multiprocessing as mp
from multiprocessing import synchronize as sync
from tqdm import tqdm

from Arena import Arena
from MCTS import MCTS
from curling.game import CurlingGame
from pytorch.NNet import NNetWrapper

log = logging.getLogger(__name__)

tqdm.monitor_interval = 0


def get_hour():
    now = time.time()
    return datetime.fromtimestamp(now).hour


class Coach():
    """
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. args are specified in main.py.
    """

    def __init__(self, GameClass, NNetWrapper, args):
        self.game = GameClass()
        self.NNetWrapper = NNetWrapper
        log.info('Loading Neural Net 1')
        self.nnet = NNetWrapper(self.game)
        log.info('Loading Neural Net 2')
        self.pnet = NNetWrapper(self.game)  # the competitor network
        self.args = args
        self.mcts = MCTS(self.game, self.nnet, self.args)
        self.trainExamplesHistory = []  # history of examples from args.numItersForTrainExamplesHistory latest iterations
        self.skipFirstSelfPlay = False  # can be overriden in loadTrainExamples()

        if args.load_model:
            log.info('Loading checkpoint...')
            self.nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])
        else:
            log.warning('Not loading a checkpoint!')

    def learn(self):
        """
        Performs numIters iterations with numEps episodes of self-play in each
        iteration. After every iteration, it retrains neural network with
        examples in trainExamples (which has a maximum length of maxlenofQueue).
        It then pits the new neural network against the old one and accepts it
        only if it wins >= updateThreshold fraction of games.
        """

        for i in range(1, self.args.numIters + 1):
            # if 8 < get_hour() < 23:
            #    log.warning('Sleeping to save CPU...')
            #    while 8 < get_hour() < 23:
            #        time.sleep(60)
            # bookkeeping
            print('------ITER ' + str(i) + '------')
            # examples of the iteration
            if not self.skipFirstSelfPlay or i > 1:
                spawn = mp.get_context('spawn')
                manager = mp.Manager()
                examples = manager.list()
                lock = mp.Lock()

                self.nnet.nnet.share_memory()

                processes = []
                sema = mp.Semaphore(self.args.parallel)
                log.info(f'Scheduling {self.args.numEps} episodes...')
                for i in range(self.args.numEps):
                    process = spawn.Process(target=_execute_episode,
                                            args=(self.nnet, self.args, examples, lock, sema))
                    processes.append(process)

                for p in tqdm(processes, desc="Starting Self Play", ncols=100):
                    p.start()

                for p in tqdm(processes, desc="Awaiting Self Play", ncols=100):
                    p.join()

                # save the iteration examples to the history 
                self.trainExamplesHistory.append(examples)

            if len(self.trainExamplesHistory) > self.args.numItersForTrainExamplesHistory:
                print("len(trainExamplesHistory) =", len(self.trainExamplesHistory),
                      " => remove the oldest trainExamples")
                self.trainExamplesHistory.pop(0)
            # backup history to a file
            # NOTE! the examples were collected using the model from the previous iteration, so (i-1)  
            self.saveTrainExamples(i - 1)

            # shuffle examples before training
            trainExamples = []
            for e in self.trainExamplesHistory:
                trainExamples.extend(e)
            random.seed(time.time())
            random.shuffle(trainExamples)

            # training new network, keeping a copy of the old one
            self.nnet.save_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            self.pnet.load_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            pmcts = MCTS(self.game, self.pnet, self.args)

            self.nnet.train(trainExamples)
            nmcts = MCTS(self.game, self.nnet, self.args)

            print('PITTING AGAINST PREVIOUS VERSION')
            arena = Arena(lambda x: np.argmax(pmcts.getActionProb(x, temp=0)),
                          lambda x: np.argmax(nmcts.getActionProb(x, temp=0)), self.game)
            pwins, nwins = arena.playGames(self.args.arenaCompare)

            print()
            print('Results')
            print(f'Won: {nwins}')
            print(f'Lost: {pwins}')
            if pwins + nwins == 0 or float(nwins) / (pwins + nwins) < self.args.updateThreshold:
                print('REJECTING NEW MODEL')
            else:
                print('ACCEPTING NEW MODEL')
                self.nnet.save_checkpoint(folder=self.args.checkpoint,
                                          filename='checkpoint_best.pth.tar')
                self.saveTrainExamples('best')
            self.nnet.save_checkpoint(folder=self.args.checkpoint, filename=self.getCheckpointFile(i))

    def getCheckpointFile(self, iteration):
        return 'checkpoint_' + str(iteration) + '.pth.tar'

    def saveTrainExamples(self, iteration):
        folder = self.args.checkpoint
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(iteration) + ".examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.trainExamplesHistory)

    def loadTrainExamples(self):
        modelFile = os.path.join(self.args.load_folder_file[0], self.args.load_folder_file[1])
        examplesFile = modelFile + ".examples"
        if not os.path.isfile(examplesFile):
            print(examplesFile)
            r = input("File with trainExamples not found. Continue? [y|n]")
            if r != "y":
                sys.exit()
        else:
            log.debug("File with trainExamples found. Read it.")
            with open(examplesFile, "rb") as f:
                self.trainExamplesHistory = Unpickler(f).load()
            # examples based on the model were already collected (loaded)
            self.skipFirstSelfPlay = True

def _execute_episode(nnet, args, results: list, lock: sync.Lock, sema: sync.Semaphore):
    """
    This function executes one episode of self-play, starting with player 1.
    As the game is played, each turn is added as a training example to
    train_examples. The game is played till the game ends. After the game
    ends, the outcome of the game is used to assign values to each example
    in train_examples.

    It uses a temp=1 if episodeStep < tempThreshold, and thereafter
    uses temp=0.

    Populates:
        results: a list of examples of the form (canonicalBoard,pi,v)
                       pi is the MCTS informed policy vector, v is +1 if
                       the player eventually won the game, else -1.
    """
    sema.acquire()
    lock.acquire()
    train_examples = []
    board = CurlingGame.getInitBoard()
    player = 1
    episode_step = 0

    result = 0
    game = CurlingGame()
    mcts = MCTS(game, nnet, args)

    for _ in range(16):
        episode_step += 1
        canonicalBoard = game.getCanonicalForm(board, player)
        temp = int(episode_step < args.tempThreshold)

        lock.release()
        pi = mcts.getActionProb(canonicalBoard, temp=temp, progressbar=False)
        lock.acquire()

        sym = game.getSymmetries(canonicalBoard, pi)
        for b, p in sym:
            train_examples.append([b, player, p, None])

        np.random.seed(int(time.time()))
        action = np.random.choice(len(pi), p=pi)
        board, player = game.getNextState(board, player, action)

        result = game.getGameEnded(board, player)

    assert result != 0
    results += [(x[0], x[2], result * ((-1) ** (x[1] != player))) for x in train_examples]
    del results[:-args.maxlenOfQueue]
    lock.release()
    sema.release()
