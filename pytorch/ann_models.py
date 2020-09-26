import logging

import torch
import torch.nn.functional as F
from torch import nn as nn

from Game import Game


class Model(nn.Sequential):
    def __init__(self, game: Game, args):
        self.args = args
        logging.info(f"Creating ANN with {args.layers} layers")
        self.board_x, self.board_y = game.getBoardSize()
        in_features = self.board_y
        height = 128
        self.out_features = game.getActionSize()
        hidden_layers = [torch.nn.Linear(height, height) for _ in range(args.layers)]
        super().__init__(
            torch.nn.Linear(in_features, height),
            *hidden_layers,
            torch.nn.Linear(height, self.out_features),
        )

        logging.debug(f"Created ANN model: %s", str(self))

    def forward(self, s: torch.Tensor):
        logging.debug(f's.size: {s.size()}')

        s = super().forward(s)

        logging.debug(f's.size: {s.size()}')  # [1, 34, 182]

        s_flat = s.flatten()

        size = s_flat.size()[0]
        s_flat = s_flat.view(-1, size)
        fc_pi = nn.Linear(size, self.out_features)
        fc_v = nn.Linear(size, 1)

        fc_pi = fc_pi.to(s_flat.device)
        fc_v = fc_v.to(s_flat.device)

        pi = fc_pi(s_flat)
        v = fc_v(s_flat)
        logging.debug('Returning %s %s', pi.size(), v.size())

        return F.log_softmax(pi, dim=1), torch.tanh(v)
