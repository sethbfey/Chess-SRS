# src/launch.py
# desc: launches the app

import chess
from nicegui import ui
from interface import draw_board

@ui.page("/")
def main_page():
    # example position
    draw_board(chess.Board("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"))


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()