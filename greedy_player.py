from basic_logic import *
from loguru import logger

class GreedyPlayer:
    def choose_move(self, board):
        moves = list(board.legal_moves)
        random.shuffle(moves)
        best_move = None
        for move in moves:
            board.push(move)
            if board.is_game_over(claim_draw=True):
                score = KING_COST if board.is_checkmate() else 0
            else:
                score = -eval_board(board, consider_check_danger = self.consider_king_safety)
            board.pop()
            if best_move == None or score > best_score:
                best_score = score
                best_move = move
        logger.success(f'GreedyPlayer move: {board.san(best_move)}')
        return best_move