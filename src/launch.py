# src/launch.py
# desc: launches the app

import chess
from nicegui import app, ui
from interface import BoardState, draw_board, flip_board, DARK_SQUARE_COLOR
from study_import import import_repertoire
from scheduler import load_cards, count_due_and_new_positions
from drill import Drill

PANEL_HEADING_STYLE = (
    "font-size: 13px; "
    "font-weight: 600; "
    "letter-spacing: 1px; "
    "text-transform: uppercase; "
    "color: #888;"
)

COUNT_UPDATE_SECONDS = 1.0

repertoire = {}


def load_repertoire():
    repertoire.update(import_repertoire())


app.on_startup(load_repertoire)


def draw_count_row(name):
    with ui.row().style("width: 100%; justify-content: space-between;"):
        ui.label(name)
        return ui.label("0").style("font-weight: 600;")


def draw_button(text, on_click):
    ui.button(text, on_click=on_click, color=DARK_SQUARE_COLOR).props("unelevated no-caps").style("width: 100%;")


@ui.page("/")
def main_page():
    board_state = BoardState()
    drill = Drill(board_state)

    cards = {
        chess.WHITE: load_cards("white"),
        chess.BLACK: load_cards("black"),
    }
    due_labels = {}
    new_labels = {}


    def update_counts():
        for color in [chess.WHITE, chess.BLACK]:
            due_count, new_count = count_due_and_new_positions(repertoire[color], cards[color], color)
            due_labels[color].text = str(due_count)
            new_labels[color].text = str(new_count)


    def drill_mode_text(color_word):
        if drill.focus_moves:
            return f"Focus {color_word}"
        return f"Drilling {color_word}"


    def on_start_white_click():
        drill.start(repertoire[chess.WHITE], chess.WHITE, cards[chess.WHITE])
        mode_label.text = drill_mode_text("White")


    def on_start_black_click():
        drill.start(repertoire[chess.BLACK], chess.BLACK, cards[chess.BLACK])
        mode_label.text = drill_mode_text("Black")


    def on_clear_click():
        drill.stop()
        mode_label.text = "Free play"


    def on_flip_click():
        flip_board(board_state)


    with ui.row().style("gap: 24px; align-items: flex-start;"):
        draw_board(board_state)

        with ui.card().style("width: 220px; gap: 12px;"):
            ui.label("White").style(PANEL_HEADING_STYLE)
            due_labels[chess.WHITE] = draw_count_row("Due now")
            new_labels[chess.WHITE] = draw_count_row("New")

            ui.separator()
            ui.label("Black").style(PANEL_HEADING_STYLE)
            due_labels[chess.BLACK] = draw_count_row("Due now")
            new_labels[chess.BLACK] = draw_count_row("New")

            ui.separator()
            ui.label("Drill").style(PANEL_HEADING_STYLE)
            mode_label = draw_count_row("Mode")
            mode_label.text = "Free play"
            draw_button("Start White", on_start_white_click)
            draw_button("Start Black", on_start_black_click)
            draw_button("Hint", drill.show_hint)
            draw_button("Clear", on_clear_click)

            ui.separator()
            draw_button("Flip board", on_flip_click)

    update_counts()
    ui.timer(COUNT_UPDATE_SECONDS, update_counts)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()