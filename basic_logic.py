import chess
import random
from loguru import logger

PAWN_COST   = 100
KNIGHT_COST = 300
BISHOP_COST = 300
ROOK_COST   = 500
QUEEN_COST  = 900
KING_COST   = 20000
HALF_KING_COST = KING_COST // 2
PIECE_COSTS = [None, PAWN_COST, KNIGHT_COST, BISHOP_COST, ROOK_COST, QUEEN_COST, KING_COST]

BB_HOME_RANKS = [ chess.BB_RANK_8, chess.BB_RANK_1 ]

STAY_HOME_RANK_PENALTY = 15
DOUBLED_PAWNS_PENALTY = 50

LARGE_CENTER_SQUARES = []
for file in [2, 3, 4, 5]:
    for rank in [2, 3, 4, 5]:
        LARGE_CENTER_SQUARES.append(chess.square(file, rank))
BB_LARGE_CENTER = chess.SquareSet(LARGE_CENTER_SQUARES)

PAWN_PROGRESS = [
    # BLACK
    [
        (chess.BB_RANK_2, 70),
        (chess.BB_RANK_3, 50),
        (chess.BB_RANK_4, 30),
        (chess.SquareSet(chess.BB_RANK_5) & BB_LARGE_CENTER, 20),
        (chess.SquareSet(chess.BB_RANK_6) & BB_LARGE_CENTER, 10)
    ],
    # WHITE
    [
        (chess.BB_RANK_7, 70),
        (chess.BB_RANK_6, 50),
        (chess.BB_RANK_5, 30),
        (chess.SquareSet(chess.BB_RANK_4) & BB_LARGE_CENTER, 20),
        (chess.SquareSet(chess.BB_RANK_3) & BB_LARGE_CENTER, 10)
    ]
]

class Threat:
    def __init__(self, from_square, to_square, cost):
        self.from_square = from_square
        self.to_square = to_square
        self.cost = cost
    def __repr__(self):
        return f'Threat({chess.SQUARE_NAMES[self.from_square]}->{chess.SQUARE_NAMES[self.to_square]}, {self.cost})'

def calc_current_turn_threats(board):
    threats = []
    for move in board.legal_moves:
        piece = board.piece_at(move.to_square)
        if not piece:
            continue
        board.push(move)
        balance = PIECE_COSTS[piece.piece_type] - calc_change(board, move.to_square)
        board.pop()
        if balance > 0:
            threats.append(Threat(move.from_square, move.to_square, balance))
    return threats

def calc_change(board, square):
    moves = [m for m in board.legal_moves if m.to_square == square]
    if len(moves) == 0:
        return 0
    min_cost = min(PIECE_COSTS[board.piece_type_at(m.from_square)] for m in moves)
    moves = [m for m in moves if PIECE_COSTS[board.piece_type_at(m.from_square)] == min_cost]
    balance = PIECE_COSTS[board.piece_type_at(square)]
    board.push(random.choice(moves))
    balance -= calc_change(board, square)
    board.pop()
    return max(0, balance)

def eval_board(board, *, consider_check_danger=False):
    if board.is_game_over():
        return -KING_COST if board.is_checkmate() else 0
    score = 0
    for color in [ chess.WHITE, chess.BLACK ]:
        sgn = 1 if color == board.turn else -1
        # PAWNS
        mask = board.pieces(chess.PAWN, color)
        score += sgn * PAWN_COST * len(mask)
        for pmask, pscore in PAWN_PROGRESS[color]:
            score += sgn * pscore * len(mask & pmask)
        for fmask in chess.BB_FILES:
            if len(mask & fmask) > 1:
                score -= sgn * DOUBLED_PAWNS_PENALTY
        # KNIGHTS
        mask = board.pieces(chess.KNIGHT, color)
        score += sgn * KNIGHT_COST * len(mask)
        score -= sgn * STAY_HOME_RANK_PENALTY * len(mask & BB_HOME_RANKS[color])
        # BISHOPS
        mask = board.pieces(chess.BISHOP, color)
        score += sgn * BISHOP_COST * len(mask)
        score -= sgn * STAY_HOME_RANK_PENALTY * len(mask & BB_HOME_RANKS[color])
        # ROOKS
        mask = board.pieces(chess.ROOK, color)
        score += sgn * ROOK_COST * len(mask)
        # QUEEN
        mask = board.pieces(chess.QUEEN, color)
        score += sgn * QUEEN_COST * len(mask)
    logger.trace(f'basic score = {score}')
    my_threats = calc_current_turn_threats(board)
    if consider_check_danger:
        d = calc_check_danger(board)
        logger.trace(f'my check score = {d}')
        score += d
    if board.is_check():
        board.push(random.choice(list(board.legal_moves)))
    else:
        board.push(chess.Move.null())
    op_threats = calc_current_turn_threats(board)
    if consider_check_danger:
        d = calc_check_danger(board)
        logger.trace(f'op check score = {d}')
        score -= d
    board.pop()
    if len(my_threats) > 0:
        d = int(0.85 * max(t.cost for t in my_threats))
        logger.trace(f'my threats score = {d}')
        score += d
    if len(op_threats) > 0:
        d = int(0.08 * max(t.cost for t in op_threats))
        logger.trace(f'op threats score = {d}')
        score -= d
    return score

def calc_check_danger(board):
    checker_squares = []
    for move in board.legal_moves:
        if move.from_square in checker_squares:
            continue
        if not board.gives_check(move):
            continue
        cap = board.piece_at(move.to_square)
        cap = PIECE_COSTS[cap.piece_type] if cap else 0
        board.push(move)
        if calc_change(board, move.to_square) <= cap:
            checker_squares.append(move.from_square)
        board.pop()
    ret = 0
    for s in checker_squares:
        if board.piece_type_at(s) == chess.QUEEN:
            ret += 8
        else:
            ret += 17
    return ret