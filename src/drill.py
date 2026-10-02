# src/drill.py
# desc: runs a drill

import chess
from nicegui import ui
from interface import update_board, flip_board, start_wrong_move_flash, stop_wrong_move_flash, play_sound, push_move_with_sound
from position_graph import position_key
from scheduler import choose_opponent_move, grade_result

OPPONENT_PAUSE_SECONDS = 0.5
WRONG_MOVE_FLASH_SECONDS = 1.5


class Drill:
    def __init__(self, board_state):
        self.board_state = board_state
        self.position_graph = None
        self.my_color = None
        self.expected_move = None
        self.hint_level = 0
        self.wrong_try_count = 0
        self.results = []


    def start(self, position_graph, my_color):
        self.position_graph = position_graph
        self.my_color = my_color
        self.results = []

        board_state = self.board_state
        board_state.board.reset()
        board_state.selected_square = None
        board_state.hint_square = None
        board_state.hint_destination_square = None
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
            self.hint_level = 0
            self.wrong_try_count = 0
            self.board_state.accepts_clicks = True

        else:
            self.expected_move = None
            self.board_state.accepts_clicks = False
            ui.timer(OPPONENT_PAUSE_SECONDS, self.play_opponent_move, once=True)


    def play_move(self, move):
        push_move_with_sound(self.board_state, move)
        self.board_state.hint_square = None
        self.board_state.hint_destination_square = None
        update_board(self.board_state)


    def play_opponent_move(self):
        board = self.board_state.board

        if board.turn == self.my_color:
            return

        move_uci = choose_opponent_move(self.position_graph, position_key(board))
        self.play_move(chess.Move.from_uci(move_uci))
        self.advance()


    def flash_wrong_move(self, square):
        start_wrong_move_flash(self.board_state, square)
        play_sound(self.board_state, "wrong")

        def stop_flash():
            stop_wrong_move_flash(self.board_state, square)

        ui.timer(WRONG_MOVE_FLASH_SECONDS, stop_flash, once=True)


    def record_result(self):
        result = {
            "position_key": position_key(self.board_state.board),
            "wrong_try_count": self.wrong_try_count,
            "hint_level": self.hint_level,
            "grade": grade_result(self.wrong_try_count, self.hint_level),
        }
        self.results.append(result)
        print(result) # temp until FSRS


    def handle_my_move(self, move):
        if move == self.expected_move:
            self.record_result()
            self.play_move(move)
            self.advance()

        elif move in self.board_state.board.legal_moves:
            self.wrong_try_count += 1
            self.flash_wrong_move(move.from_square)


    def show_hint(self):
        if self.expected_move is None:
            return

        if self.hint_level < 2:
            self.hint_level += 1

        self.board_state.hint_square = self.expected_move.from_square
        if self.hint_level == 2:
            self.board_state.hint_destination_square = self.expected_move.to_square

        update_board(self.board_state)