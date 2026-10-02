# src/interface.py
# desc: creates UI

import chess
from pathlib import Path
from nicegui import ui

PIECES_FOLDER = Path(__file__).parent / "assets" / "pieces"
SOUNDS_FOLDER = Path(__file__).parent / "assets" / "sounds"

LIGHT_SQUARE_COLOR = "#EBECD0"
DARK_SQUARE_COLOR = "#739552"

LIGHT_HIGHLIGHT_COLOR = "#F5F682"
DARK_HIGHLIGHT_COLOR = "#B9CA43"

HINT_COLOR = "#52B0DC"

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

PIECE_STYLE = "width: 100px; height: 100px; pointer-events: none;"
PIECE_CSS = ".chess-piece svg { width: 100%; height: 100%; display: block; }"

WRONG_MOVE_CSS = (
    "@keyframes wrong-move-flash-light { "
    "0%, 100% { background-color: #EBECD0; } "
    "50% { background-color: #EB7D6A; } } "
    "@keyframes wrong-move-flash-dark { "
    "0%, 100% { background-color: #739552; } "
    "50% { background-color: #D36C50; } } "
    ".wrong-move-flash-light { animation: wrong-move-flash-light 0.5s 3; } "
    ".wrong-move-flash-dark { animation: wrong-move-flash-dark 0.5s 3; }"
    ".wrong-move-flash-light .square-coordinate { color: #739552 !important; }"
)


class BoardState:
    def __init__(self):
        self.board = chess.Board()
        self.white_at_bottom = True
        self.selected_square = None

        self.accepts_clicks = True
        self.on_move_attempted = None
        self.hint_square = None
        self.hint_destination_square = None
        self.sound_players = {}

        self.board_column = None
        self.board_rows = []
        self.square_elements = {}
        self.piece_elements = {}
        self.coordinate_elements = {}


def load_piece_svgs():
    piece_svgs = {}
    for color_letter in ["w", "b"]:
        for piece_letter in ["K", "Q", "R", "B", "N", "P"]:
            svg_path = PIECES_FOLDER / f"{color_letter}{piece_letter}.svg"

            if color_letter == "w":
                symbol = piece_letter
            else:
                symbol = piece_letter.lower()

            piece_svgs[symbol] = svg_path.read_text()

    return piece_svgs


PIECE_SVGS = load_piece_svgs()


def create_move(board, from_square, to_square):
    moving_piece = board.piece_at(from_square)
    to_rank = chess.square_rank(to_square)

    is_pawn = moving_piece.piece_type == chess.PAWN
    reaches_last_rank = to_rank == 0 or to_rank == 7

    if is_pawn and reaches_last_rank:
        return chess.Move(from_square, to_square, promotion=chess.QUEEN)

    return chess.Move(from_square, to_square)


def push_move_with_sound(board_state, move):
    if board_state.board.is_capture(move):
        sound_name = "capture"
    else:
        sound_name = "move"

    board_state.board.push(move)
    play_sound(board_state, sound_name)


def play_free_move(board_state, move):
    if move in board_state.board.legal_moves:
        push_move_with_sound(board_state, move)


def handle_square_click(board_state, clicked_square):
    if not board_state.accepts_clicks:
        return

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
        board_state.selected_square = None

        if board_state.on_move_attempted is None:
            play_free_move(board_state, move)
        else:
            board_state.on_move_attempted(move)

    update_board(board_state)


def create_click_handler(board_state, square):
    def on_square_click():
        handle_square_click(board_state, square)

    return on_square_click


def is_dark_square(square):
    file_index = chess.square_file(square)
    rank_index = chess.square_rank(square)
    return (file_index + rank_index) % 2 == 0


def square_background_color(square, is_highlighted):
    if is_dark_square(square):
        if is_highlighted:
            return DARK_HIGHLIGHT_COLOR
        return DARK_SQUARE_COLOR

    if is_highlighted:
        return LIGHT_HIGHLIGHT_COLOR
    return LIGHT_SQUARE_COLOR


def coordinate_text_color(square, is_highlighted):
    if is_dark_square(square) and not is_highlighted:
        return LIGHT_SQUARE_COLOR
    return DARK_SQUARE_COLOR


def draw_board(board_state):
    ui.add_css(PIECE_CSS)
    ui.add_css(WRONG_MOVE_CSS)

    for sound_name in ["move", "capture", "wrong"]:
        sound_path = SOUNDS_FOLDER / f"{sound_name}.mp3"
        board_state.sound_players[sound_name] = ui.audio(sound_path, controls=False)

    board_state.board_column = ui.column().style("gap: 0")
    with board_state.board_column:
        for rank_index in [7, 6, 5, 4, 3, 2, 1, 0]:
            board_row = ui.row().style("gap: 0; flex-wrap: nowrap")
            board_state.board_rows.append(board_row)

            with board_row:
                for file_index in [0, 1, 2, 3, 4, 5, 6, 7]:
                    square = chess.square(file_index, rank_index)
                    coordinate = chess.square_name(square).upper()

                    square_element = ui.element("div").style(SQUARE_STYLE)
                    square_element.on("click", create_click_handler(board_state, square))

                    with square_element:
                        piece_element = ui.html("", sanitize=False).classes("chess-piece").style(PIECE_STYLE)
                        coordinate_element = ui.label(coordinate).classes("square-coordinate").style(COORDINATE_STYLE)

                    board_state.square_elements[square] = square_element
                    board_state.piece_elements[square] = piece_element
                    board_state.coordinate_elements[square] = coordinate_element

    update_board(board_state)


def update_board(board_state):
    last_move_squares = []
    if board_state.board.move_stack:
        last_move = board_state.board.peek()
        last_move_squares = [last_move.from_square, last_move.to_square]

    for square in chess.SQUARES:
        is_selected = square == board_state.selected_square
        is_last_move_square = square in last_move_squares
        is_hint_piece_square = square == board_state.hint_square
        is_hint_destination_square = square == board_state.hint_destination_square
        is_hint_square = is_hint_piece_square or is_hint_destination_square
        is_highlighted = is_selected or is_last_move_square

        square_color = square_background_color(square, is_highlighted)
        text_color = coordinate_text_color(square, is_highlighted)

        if is_hint_square:
            square_color = HINT_COLOR
            text_color = LIGHT_SQUARE_COLOR

        board_state.square_elements[square].style(f"background-color: {square_color}")
        board_state.coordinate_elements[square].style(f"color: {text_color}")

        piece = board_state.board.piece_at(square)
        if piece is None:
            board_state.piece_elements[square].content = ""
        else:
            board_state.piece_elements[square].content = PIECE_SVGS[piece.symbol()]


def wrong_move_flash_class(square):
    if is_dark_square(square):
        return "wrong-move-flash-dark"
    return "wrong-move-flash-light"


def start_wrong_move_flash(board_state, square):
    board_state.square_elements[square].classes(add=wrong_move_flash_class(square))


def stop_wrong_move_flash(board_state, square):
    board_state.square_elements[square].classes(remove=wrong_move_flash_class(square))


def flip_board(board_state):
    board_state.white_at_bottom = not board_state.white_at_bottom

    if board_state.white_at_bottom:
        column_direction = "column"
        row_direction = "row"
    else:
        column_direction = "column-reverse"
        row_direction = "row-reverse"

    board_state.board_column.style(f"flex-direction: {column_direction}")
    for board_row in board_state.board_rows:
        board_row.style(f"flex-direction: {row_direction}")


def play_sound(board_state, sound_name):
    board_state.sound_players[sound_name].play()