# src/interface.py
# desc: creates UI

import chess
from pathlib import Path
from nicegui import ui

PIECES_FOLDER = Path(__file__).parent / "assets" / "pieces"

LIGHT_SQUARE_COLOR = "#EBECD0"
DARK_SQUARE_COLOR = "#739552"

SQUARE_STYLE = (
    "width: 100px; "
    "height: 100px; "
    "position: relative; "
)

COORDINATE_STYLE = (
    "position: absolute; "
    "top: 2px; "
    "right: 5px; "
    "font-weight: bold; "
)

PIECE_STYLE = "width: 100px; height: 100px;"

ranks = ["1", "2", "3", "4", "5", "6", "7", "8"]
files = ["A", "B", "C", "D", "E", "F", "G", "H"]


def piece_image_path(piece):
    if piece.color == chess.WHITE:
        color_letter = "w"
    else:
        color_letter = "b"

    piece_letter = piece.symbol().upper()
    return PIECES_FOLDER / f"{color_letter}{piece_letter}.svg"


def draw_board(board):
    with ui.column().style("gap: 0"):
        for row_from_top, rank in enumerate(ranks[::-1]):
            with ui.row().style("gap: 0"):
                for file_index, file in enumerate(files):
                    coordinate = f"{file}{rank}"
                    rank_index = 7 - row_from_top
                    square = chess.square(file_index, rank_index)

                    if (row_from_top + file_index) % 2 == 0:
                        square_color = LIGHT_SQUARE_COLOR
                        text_color = DARK_SQUARE_COLOR
                    else:
                        square_color = DARK_SQUARE_COLOR
                        text_color = LIGHT_SQUARE_COLOR

                    square_style = SQUARE_STYLE + f"background-color: {square_color};"

                    with ui.element("div").style(square_style):
                        piece = board.piece_at(square)
                        if piece is not None:
                            ui.image(piece_image_path(piece)).style(PIECE_STYLE)

                        ui.label(coordinate).style(COORDINATE_STYLE + f"color: {text_color};")