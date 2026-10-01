# src/interface.py
# desc: creates UI

import chess
from pathlib import Path
from nicegui import ui

PIECES_FOLDER = Path(__file__).parent / "assets" / "pieces"

LIGHT_SQUARE_COLOR = "#EBECD0"
DARK_SQUARE_COLOR = "#739552"
SELECTED_SQUARE_COLOR = "#F5F682"

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


class BoardState:
    def __init__(self):
        self.board = chess.Board()
        self.white_at_bottom = True
        self.selected_square = None


def piece_image_path(piece):
    if piece.color == chess.WHITE:
        color_letter = "w"
    else:
        color_letter = "b"

    piece_letter = piece.symbol().upper()
    return PIECES_FOLDER / f"{color_letter}{piece_letter}.svg"


def create_move(board, from_square, to_square):
    moving_piece = board.piece_at(from_square)
    to_rank = chess.square_rank(to_square)

    is_pawn = moving_piece.piece_type == chess.PAWN
    reaches_last_rank = to_rank == 0 or to_rank == 7

    if is_pawn and reaches_last_rank:
        #TODO user promotion
        return chess.Move(from_square, to_square, promotion=chess.QUEEN)

    return chess.Move(from_square, to_square)


def handle_square_click(board_state, clicked_square):
    board = board_state.board
    clicked_piece = board.piece_at(clicked_square)
    clicked_own_piece = clicked_piece is not None and clicked_piece.color == board.turn

    if board_state.selected_square is None:
        if clicked_own_piece:
            board_state.selected_square = clicked_square

    elif clicked_square == board_state.selected_square:
        board_state.selected_square = None

    elif clicked_own_piece:
        board_state.selected_square = clicked_square

    else:
        move = create_move(board, board_state.selected_square, clicked_square)
        if move in board.legal_moves:
            board.push(move)
        board_state.selected_square = None

    draw_board.refresh()


def create_click_handler(board_state, square):
    def on_square_click():
        handle_square_click(board_state, square)

    return on_square_click


@ui.refreshable
def draw_board(board_state):
    if board_state.white_at_bottom:
        rank_indexes_top_to_bottom = [7, 6, 5, 4, 3, 2, 1, 0]
        file_indexes_left_to_right = [0, 1, 2, 3, 4, 5, 6, 7]
    else:
        rank_indexes_top_to_bottom = [0, 1, 2, 3, 4, 5, 6, 7]
        file_indexes_left_to_right = [7, 6, 5, 4, 3, 2, 1, 0]

    with ui.column().style("gap: 0"):
        for rank_index in rank_indexes_top_to_bottom:
            with ui.row().style("gap: 0"):
                for file_index in file_indexes_left_to_right:
                    square = chess.square(file_index, rank_index)
                    coordinate = chess.square_name(square).upper()

                    if (file_index + rank_index) % 2 == 0:
                        square_color = DARK_SQUARE_COLOR
                        text_color = LIGHT_SQUARE_COLOR
                    else:
                        square_color = LIGHT_SQUARE_COLOR
                        text_color = DARK_SQUARE_COLOR

                    if square == board_state.selected_square:
                        square_color = SELECTED_SQUARE_COLOR

                    square_style = SQUARE_STYLE + f"background-color: {square_color};"
                    square_element = ui.element("div").style(square_style)
                    square_element.on("click", create_click_handler(board_state, square))

                    with square_element:
                        piece = board_state.board.piece_at(square)
                        if piece is not None:
                            ui.image(piece_image_path(piece)).style(PIECE_STYLE)

                        ui.label(coordinate).style(COORDINATE_STYLE + f"color: {text_color};")


def flip_board(board_state):
    board_state.white_at_bottom = not board_state.white_at_bottom
    draw_board.refresh()