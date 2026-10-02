# src/scheduler.py
# desc: FSRS grades, due positions, picking which line to play

import random


def choose_opponent_move(position_graph, key):
    # random choice for now
    return random.choice(list(position_graph[key]))