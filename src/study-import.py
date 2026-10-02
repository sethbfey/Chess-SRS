# src/study-import.py
# desc: downloads my white and black repertoire studies from Lichess

from urllib.request import urlopen

WHITE_STUDY_ID = "GG9rv9PT"
BLACK_STUDY_ID = "HQqyxSPH"
STUDY_EXPORT_URL = "https://lichess.org/api/study/{study_id}.pgn?comments=false&clocks=false"

def download_study_pgn(study_id):
    url = STUDY_EXPORT_URL.format(study_id=study_id)
    with urlopen(url, timeout=10) as response:
        return response.read().decode("utf-8")


if __name__ == "__main__":
    # temp until auto import
    import chess
    from position_graph import build_position_graph, count_my_positions

    white_graph = build_position_graph(download_study_pgn(WHITE_STUDY_ID))
    black_graph = build_position_graph(download_study_pgn(BLACK_STUDY_ID))

    print(f"White: {len(white_graph)} positions, {count_my_positions(white_graph, chess.WHITE)} with my answer")
    print(f"Black: {len(black_graph)} positions, {count_my_positions(black_graph, chess.BLACK)} with my answer")