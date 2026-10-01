# src/launch.py
# desc: launches the app

import chess
from nicegui import ui
from interface import BoardState, draw_board, flip_board

@ui.page("/")
def main_page():
    # example position
    board_state = BoardState()
    board_state.board = chess.Board("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3")

    def on_flip_click():
        flip_board(board_state)

    draw_board(board_state)
    ui.button("Flip board", on_click=on_flip_click)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()