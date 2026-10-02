# src/launch.py
# desc: launches the app

import chess
from nicegui import app, ui
from interface import BoardState, draw_board, flip_board, DARK_SQUARE_COLOR
from position_graph import count_my_positions
from study_import import import_repertoire

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


@ui.page("/")
def main_page():
    board_state = BoardState()

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
            ui.button("Flip board", on_click=on_flip_click, color=DARK_SQUARE_COLOR).props("unelevated no-caps").style("width: 100%;")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()