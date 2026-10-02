# src/launch.py
# desc: launches the app

import chess
from nicegui import app, ui
from interface import BoardState, draw_board, flip_board, DARK_SQUARE_COLOR
from position_graph import count_my_positions
from study_import import import_repertoire
from drill import Drill

PANEL_HEADING_STYLE = (
    "font-size: 13px; "
    "font-weight: 600; "
    "letter-spacing: 1px; "
    "text-transform: uppercase; "
    "color: #888;"
)

repertoire = {}


def load_repertoire():
    repertoire.update(import_repertoire())


app.on_startup(load_repertoire)


def draw_count_row(name, count):
    with ui.row().style("width: 100%; justify-content: space-between;"):
        ui.label(name)
        ui.label(str(count)).style("font-weight: 600;")


def draw_button(text, on_click):
    ui.button(text, on_click=on_click, color=DARK_SQUARE_COLOR).props("unelevated no-caps").style("width: 100%;")


@ui.page("/")
@ui.page("/")
def main_page():
    board_state = BoardState()
    drill = Drill(board_state)

    def on_start_white_click():
        drill.start(repertoire[chess.WHITE], chess.WHITE)

    def on_start_black_click():
        drill.start(repertoire[chess.BLACK], chess.BLACK)

    def on_flip_click():
        flip_board(board_state)

    with ui.row().style("gap: 24px; align-items: flex-start;"):
        draw_board(board_state)

        with ui.card().style("width: 220px; gap: 12px;"):
            ui.label("Repertoire").style(PANEL_HEADING_STYLE)

            white_position_count = count_my_positions(repertoire[chess.WHITE], chess.WHITE)
            black_position_count = count_my_positions(repertoire[chess.BLACK], chess.BLACK)
            draw_count_row("White", white_position_count)
            draw_count_row("Black", black_position_count)

            ui.separator()
            ui.label("Drill").style(PANEL_HEADING_STYLE)
            draw_button("Start White", on_start_white_click)
            draw_button("Start Black", on_start_black_click)

            ui.separator()
            draw_button("Flip board", on_flip_click)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run()