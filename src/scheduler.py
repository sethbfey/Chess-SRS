# src/scheduler.py
# desc: FSRS grades, due positions, picking which line to play

import random
import chess
from datetime import datetime, timezone
from fsrs import Scheduler, Card, Rating
from database import save_card, load_saved_cards

NEW_POSITION_NEED = 1.0
DUE_POSITION_NEED = 1.0
NOT_DUE_POSITION_NEED = 0.1

fsrs_scheduler = Scheduler()


def grade_result(wrong_try_count, hint_level):
    if hint_level > 0 or wrong_try_count >= 2:
        return Rating.Again

    if wrong_try_count == 1:
        return Rating.Hard

    return Rating.Good


def load_cards(color_name):
    cards = {}
    for key, card_json in load_saved_cards(color_name):
        cards[key] = Card.from_json(card_json)
    return cards


def review_position(cards, color_name, result):
    key = result["position_key"]

    if key in cards:
        card = cards[key]
    else:
        card = Card()

    card, review_log = fsrs_scheduler.review_card(card, result["grade"])
    cards[key] = card

    save_card(color_name, key, result["move_uci"], card.to_json(), result["wrong_try_count"], result["hint_level"])
    return card


def is_my_turn(key, my_color):
    side_to_move = key.split(" ")[1]
    if my_color == chess.WHITE:
        return side_to_move == "w"
    return side_to_move == "b"


def position_need(cards, key, now):
    if key not in cards:
        return NEW_POSITION_NEED

    card = cards[key]
    if card.due <= now:
        return DUE_POSITION_NEED

    time_since_review = now - card.last_review
    scheduled_interval = card.due - card.last_review
    return NOT_DUE_POSITION_NEED * (time_since_review / scheduled_interval)


def best_line_need(position_graph, cards, key, my_color, now, known_needs):
    if key in known_needs:
        return known_needs[key]

    moves = position_graph[key]

    best_need_after_this_position = 0.0
    for next_key in moves.values():
        next_need = best_line_need(position_graph, cards, next_key, my_color, now, known_needs)
        if next_need > best_need_after_this_position:
            best_need_after_this_position = next_need

    need = best_need_after_this_position
    if moves and is_my_turn(key, my_color):
        need += position_need(cards, key, now)

    known_needs[key] = need
    return need


def choose_opponent_move(position_graph, cards, key, my_color):
    now = datetime.now(timezone.utc)
    known_needs = {}

    best_need = -1.0
    best_moves = []
    for move_uci, next_key in position_graph[key].items():
        need = best_line_need(position_graph, cards, next_key, my_color, now, known_needs)
        if need > best_need:
            best_need = need
            best_moves = [move_uci]
        elif need == best_need:
            best_moves.append(move_uci)

    print(f"line need {best_need:.2f}") # temp for now
    return random.choice(best_moves)


def count_due_and_new_positions(position_graph, cards, my_color):
    now = datetime.now(timezone.utc)
    due_count = 0
    new_count = 0

    for key, moves in position_graph.items():
        if not moves or not is_my_turn(key, my_color):
            continue

        if key not in cards:
            new_count += 1
        elif cards[key].due <= now:
            due_count += 1

    return due_count, new_count