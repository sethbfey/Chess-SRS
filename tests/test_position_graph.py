# tests/test_position_graph.py

import chess
from position_graph import build_position_graph, position_key

TRANSPOSITION_PGN = """
[Event "Line 1"]

1. Nf3 d5 2. g3 Nf6 3. Bg2 *

[Event "Line 2"]

1. g3 d5 2. Nf3 Nf6 *
"""


def test_line_ending_at_transposition_continues():
    position_graph = build_position_graph(TRANSPOSITION_PGN)

    board = chess.Board()
    for move in ["g3", "d5", "Nf3", "Nf6"]:
        board.push_san(move)

    assert "f1g2" in position_graph[position_key(board)]