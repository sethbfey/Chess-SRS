# src/study-import.py
# desc: downloads my white and black repertoire studies from Lichess

from urllib.request import urlopen
from database import save_study_pgn, load_saved_study_pgn

WHITE_STUDY_ID = "GG9rv9PT"
BLACK_STUDY_ID = "HQqyxSPH"
STUDY_EXPORT_URL = "https://lichess.org/api/study/{study_id}.pgn?comments=false&clocks=false"


def download_study_pgn(study_id):
    url = STUDY_EXPORT_URL.format(study_id=study_id)
    with urlopen(url, timeout=10) as response:
        return response.read().decode("utf-8")


def get_study_pgn(color_name, study_id):
    try:
        pgn_text = download_study_pgn(study_id)
    except OSError:
        # in case there is some Lichess or internet error
        print(f"Could not download the {color_name} study, using the saved copy")
        return load_saved_study_pgn(color_name)

    save_study_pgn(color_name, pgn_text)
    return pgn_text


if __name__ == "__main__":
    # temp until auto import
    import chess
    from position_graph import build_position_graph, count_my_positions

    white_graph = build_position_graph(get_study_pgn("white", WHITE_STUDY_ID))
    black_graph = build_position_graph(get_study_pgn("black", BLACK_STUDY_ID))

    print(f"White: {len(white_graph)} positions, {count_my_positions(white_graph, chess.WHITE)} with my answer")
    print(f"Black: {len(black_graph)} positions, {count_my_positions(black_graph, chess.BLACK)} with my answer")