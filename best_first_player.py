import chess
import random
import math
from loguru import logger
from basic_logic import eval_board, HALF_KING_COST, PAWN_COST

SCORE_WINDOW = 10
VISIT_PENALTY = 50

class BestFirstPlayer:
    def __init__(self, max_size):
        self.max_size = max_size
    def choose_move(self, board):
        root = TreeNode(None, 0)
        prev_progress = 0
        while not root.complete and root.size < self.max_size:
            progress = root.size * 100 // self.max_size
            if progress - prev_progress >= 10:
                logger.info(f'Progress: {progress}%')
                prev_progress = progress
            _print_improve_tree_path(board, root, [])
            _improve_tree(board, root)
        min_score = min(c.score for c in root.children)
        move = random.choice([c.move for c in root.children if c.score <= min_score + SCORE_WINDOW])
        logger.success(f'BestFirstPlayer move: {board.san(move)}')
        return move

class TreeNode:
    def __init__(self, move, score):
        self.move = move
        self.score = score
        self.children = None
        self.size = 1
        self.complete = False

def _improve_tree(board, node):
    if node.children == None:
        _expand_leaf(board, node)
        return
    best_child = _choose_child_to_improve(node)
    if not best_child:
        node.complete = True
        return
    board.push(best_child.move)
    _improve_tree(board, best_child)
    board.pop()
    _aggregate_children(node)

def _print_improve_tree_path(board, node, parts):
    if node.children == None:
        parts.append(str(node.score))
        logger.debug(' '.join(parts))
        return
    best_child = _choose_child_to_improve(node)
    if best_child == None:
        parts.append(str(node.score))
        logger.debug(' '.join(parts))
        return
    parts.append(board.san(best_child.move))
    board.push(best_child.move)
    _print_improve_tree_path(board, best_child, parts)
    board.pop()

def _choose_child_to_improve(node):
    best_child = None
    best_score = None
    for child in node.children:
        if child.complete:
            continue
        score = -child.score -math.log(child.size) * VISIT_PENALTY
        if not best_child or score > best_score:
            best_child = child
            best_score = score
    return best_child

def _expand_leaf(board, node):
    if board.is_game_over():
        node.score = -KING_COST if board.is_checkmate() else 0
        node.complete = True
        return
    node.children = []
    moves = list(board.legal_moves)
    random.shuffle(moves)
    for move in board.legal_moves:
        board.push(move)
        score = eval_board(board)
        board.pop()
        node.children.append(TreeNode(move, score))
    _aggregate_children(node)

def _aggregate_children(node):
    node.size = sum(c.size for c in node.children)
    node.score = -min(c.score for c in node.children)
    if node.score > HALF_KING_COST:
        node.score -= PAWN_COST
        node.complete = True
    elif node.score < -HALF_KING_COST:
        node.score += PAWN_COST
        node.complete = True