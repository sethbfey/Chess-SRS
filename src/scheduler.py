# src/scheduler.py
# desc: FSRS grades, due positions, picking which line to play

import random
from fsrs import Rating


def grade_result(wrong_try_count, hint_level):
    if hint_level > 0 or wrong_try_count >= 2:
        return Rating.Again

    if wrong_try_count == 1:
        return Rating.Hard

    return Rating.Good

def choose_opponent_move(position_graph, key):
    # random choice for now
    return random.choice(list(position_graph[key]))