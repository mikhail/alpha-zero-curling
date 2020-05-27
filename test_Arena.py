from unittest import mock

from Arena import Arena


def test_play_games_cumulative_score():
    mock_player = mock.Mock()
    mock_game = mock.Mock()
    mock_game.getGameEnded.return_value = 2
    arena = Arena(mock_player, mock_player, mock_game)
    p1_score, p2_score = arena.playGames(10, verbose=False)
    assert p1_score == 10
    assert p2_score == 10
