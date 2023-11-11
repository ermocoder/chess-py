import chess
import random
from basic_logic import eval_board, calc_current_turn_threats, KING_COST, HALF_KING_COST, PAWN_COST
from loguru import logger

class NegMaxPlayer:
    def __init__(self, search_depth):
        self.search_depth = search_depth
    def choose_move(self, board):
        _, move = dfs(board, self.search_depth, -KING_COST, KING_COST)
        logger.success(f'NegMaxPlayer move: {board.san(move)}')
        return move

SCORE_WINDOW = 10

def dfs(board, depth, min_score, max_score):
    if depth == 0:
        return dfs_tail(board, min_score, max_score), None
    if board.is_game_over(claim_draw = True):
        return (-KING_COST if board.is_checkmate() else 0), None
    moves = list(board.legal_moves)
    random.shuffle(moves)
    best_move = None
    for move in moves:
        board.push(move)
        score = -dfs(board, depth - 1, -max_score, -min_score)[0]
        board.pop()
        if score > HALF_KING_COST:
            score -= PAWN_COST
        if score < -HALF_KING_COST:
            score += PAWN_COST
        if not best_move or score > best_score + SCORE_WINDOW:
            best_move = move
            best_score = score
        best_score = max(score, best_score)
        if score >= max_score:
            return best_score, best_move
        elif score > min_score:
            min_score = score
    return best_score, best_move

def dfs_tail(board, min_score, max_score):
    if board.is_game_over(claim_draw = False):
        return -KING_COST if board.is_checkmate() else 0
    best_score = eval_board(board)
    if best_score >= max_score:
        return best_score
    elif best_score > min_score:
        min_score = best_score
    threats = calc_current_turn_threats(board)
    for move in board.legal_moves:
        if not any(t for t in threats if t.from_square == move.from_square and t.to_square == move.to_square):
            continue
        board.push(move)
        score = -dfs_tail(board, -max_score, -min_score)
        board.pop()
        if score > best_score:
            best_score = score
            if score >= max_score:
                return score
            elif score > min_score:
                min_score = score
    return best_score