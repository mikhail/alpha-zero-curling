import math

from tqdm import tqdm

tqdm.monitor_interval = 0


class Arena():
    """
    An Arena class where any 2 agents can be pit against each other.
    """

    def __init__(self, player1, player2, game, display=None):
        """
        Input:
            player 1,2: two functions that takes board as input, return action
            game: Game object
            display: a function that takes board as input and prints it (e.g.
                     display in othello/OthelloGame). Is necessary for verbose
                     mode.

        see othello/OthelloPlayers.py for an example. See pit.py for pitting
        human players/other baselines with each other.
        """
        self.player1 = player1
        self.player2 = player2
        self.game = game
        self.display = display

    def playGame(self, verbose=False):
        """
        Executes one episode of a game.

        Returns:
            either
                winner: player who won the game (1 if player1, -1 if player2)
            or
                draw result returned from the game that is neither 1, -1, nor 0.
        """
        players = [self.player2, None, self.player1]
        curPlayer = 1
        board = self.game.getInitBoard()
        total_moves = 16  # Curling
        progressbar = tqdm(total=total_moves, disable=verbose)  # Don't want a bar when pitting
        it = 0
        while self.game.getGameEnded(board, curPlayer) == 0:
            it += 1
            if verbose:
                assert self.display
                print("Turn", str(it), "Player", curPlayer)
                self.display(board)
            action = players[curPlayer + 1](self.game.getCanonicalForm(board, curPlayer))

            valids = self.game.getValidMoves(self.game.getCanonicalForm(board, curPlayer), 1)

            if valids[action] == 0:
                print(action)
                assert valids[action] > 0

            if verbose:
                print(f"Player({curPlayer}) chose action={action}")

            board, curPlayer = self.game.getNextState(board, curPlayer, action)
            progressbar.update()
        if verbose:
            assert (self.display)
            print("Game over: Turn ", str(it), "Result ", str(self.game.getGameEnded(board, 1)))
            self.display(board)
        return curPlayer * self.game.getGameEnded(board, curPlayer)

    def playGames(self, num, verbose=False):
        """
        Plays num games in which player1 starts num/2 games and player2 starts
        num/2 games.

        Returns:
            oneWon: games won by player1
            twoWon: games won by player2
            draws:  games won by nobody
        """
        p1_score = 0
        p2_score = 0
        for _ in tqdm(range(math.ceil(num / 2)), desc="Arena.playGames p1/p2"):
            res = self.playGame(verbose=verbose)
            if res == 0:
                raise Exception('WHOA playGame ended before end of game. res=%s' % res)
            if res > 0:
                p1_score += res
            else:
                p2_score -= res

        self.player1, self.player2 = self.player2, self.player1

        for _ in tqdm(range(math.floor(num / 2)), desc="Arena.playGames p2/p1"):
            res = self.playGame(verbose=verbose)
            if res == 0:
                raise Exception('WHOA playGame ended before end of game. res=%s' % res)
            if res > 0:
                p2_score += res
            else:
                p1_score -= res

        return p1_score, p2_score
