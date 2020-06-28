import logging

import torch
import torch.nn as nn
import torch.nn.functional as F


class Model(nn.Module):
    def __init__(self, game, args):
        # game params
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()
        self.args = args

        # nnet params
        layers = args.layers
        self.layers = layers
        assert layers > 2
        self.shrink = 2 * (self.layers - 2)
        logging.info(f"Creating NN with {layers} layers 🧮")
        self.conv = []
        self.batchnorm = []
        self.fc = []
        self.fcbn = []

        super(Model, self).__init__()

        self._setup()

    def _setup(self):
        # Create Conv layers
        in_channels = 1
        kernel_size = int(float(min(self.board_x, self.board_y)) / self.layers)
        # if kernel_size < 3:
        kernel_size = 3
        paddings = [0] * self.layers
        paddings[0] = 1
        paddings[1] = 1
        for i in range(self.layers):
            conv = nn.Conv2d(in_channels, self.args.num_channels, kernel_size, stride=1, padding=paddings[i])
            self.add_module(f'conv{i}', conv)
            self.conv.append(conv)
            in_channels = self.args.num_channels

        # Prepare Batch Normalization
        for i in range(self.layers):
            bn = nn.BatchNorm2d(self.args.num_channels)
            self.batchnorm.append(bn)
            self.add_module(f'batchnorm{i}', bn)

        # Prepare features
        in_features = self.args.num_channels * (self.board_x - self.shrink) * (self.board_y - self.shrink)
        if in_features <= 0:
            logging.error("Too many layers considering the board size.")
            raise ValueError

        out_features = 256 * 2 ** (self.layers - 2)
        for i in range(self.layers - 2):
            out_features = int(out_features / 2.0)  # needs to be unchanged same outside of the loop
            max_features = min(out_features, 256)
            logging.warning(f"Creating a feature with out_features: {out_features}")
            linear = nn.Linear(in_features, max_features)
            self.fc.append(linear)
            self.add_module(f'fc{i}', linear)

            bn = nn.BatchNorm1d(max_features)
            self.fcbn.append(bn)
            self.add_module(f'batchnorm1d{i}', bn)

            in_features = max_features

        self.fc_pi = nn.Linear(out_features, self.action_size)
        self.fc_v = nn.Linear(out_features, 1)

    def forward(self, s: torch.Tensor):
        s = s.view(-1, 1, self.board_x, self.board_y)

        for i in range(self.layers):
            s = F.relu(self.batchnorm[i](self.conv[i](s)))

        size = self.args.num_channels * (self.board_x - self.shrink) * (self.board_y - self.shrink)
        s = s.view(-1, size)

        for i in range(self.layers - 2):
            s = F.dropout(F.relu(self.fcbn[i](self.fc[i](s))), p=self.args.dropout, training=self.training)

        pi = self.fc_pi(s)
        v = self.fc_v(s)

        return F.log_softmax(pi, dim=1), torch.tanh(v)
