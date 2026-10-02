# src/drill.py
# desc: runs a drill

import chess
from nicegui import ui
from interface import update_board, flip_board
from position_graph import position_key
from scheduler import choose_opponent_move

OPPONENT_PAUSE_SECONDS = 0.5


class Drill:
    def __init__(self, board_state):
        self.board_state = board_state
        self.position_graph = None
        self.my_color = None
        self.expected_move = None

    def start(self, position_graph, my_color):
        self.position_graph = position_graph
        self.my_color = my_color

        board_state = self.board_state
        board_state.board.reset()
        board_state.selected_square = None
        board_state.on_move_attempted = self.handle_my_move

        my_color_is_at_bottom = board_state.white_at_bottom == (my_color == chess.WHITE)
        if not my_color_is_at_bottom:
            flip_board(board_state)

        update_board(board_state)
        self.advance()

    def advance(self):
        board = self.board_state.board
        moves = self.position_graph[position_key(board)]

        if not moves:
            self.expected_move = None
            self.board_state.accepts_clicks = False

        elif board.turn == self.my_color:
            self.expected_move = chess.Move.from_uci(list(moves)[0])
            self.board_state.accepts_clicks = True

        else:
            self.expected_move = None
            self.board_state.accepts_clicks = False
            ui.timer(OPPONENT_PAUSE_SECONDS, self.play_opponent_move, once=True)

    def play_opponent_move(self):
        board = self.board_state.board
        
        if board.turn == self.my_color:
            return

        move_uci = choose_opponent_move(self.position_graph, position_key(board))
        self.play_move(chess.Move.from_uci(move_uci))
        self.advance()

    def handle_my_move(self, move):
        if move == self.expected_move:
            self.play_move(move)
            self.advance()

    def play_move(self, move):
        self.board_state.board.push(move)
        update_board(self.board_state)