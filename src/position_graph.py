# src/position_graph.py
# desc: converts study PGN into a graph of positions

import io
import chess
import chess.pgn


def position_key(board):
    return board.epd()


def build_position_graph(pgn_text):
    position_graph = {}
    pgn_file = io.StringIO(pgn_text)

    game = chess.pgn.read_game(pgn_file)
    while game is not None:
        board = game.board()
        position_graph.setdefault(position_key(board), {})
        add_variations(position_graph, game, board)
        game = chess.pgn.read_game(pgn_file)

    return position_graph


def add_variations(position_graph, node, board):
    for variation in node.variations:
        from_key = position_key(board)
        board.push(variation.move)
        to_key = position_key(board)

        position_graph[from_key][variation.move.uci()] = to_key
        position_graph.setdefault(to_key, {})

        add_variations(position_graph, variation, board)
        board.pop()