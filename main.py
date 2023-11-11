import chess
import chess.svg
from IPython.display import display
from loguru import logger
import sys
from best_first_player import BestFirstPlayer
from human_player import HumanPlayer
import random


def main():
    human = HumanPlayer()
    pc = BestFirstPlayer(3000)
    play(human, pc, orientation=chess.WHITE, print_ascii=True)

def play(whites_player, blacks_player, *,
         start_board=None,
         log_level='INFO',
         orientation=chess.WHITE,
         print_svg=False, 
         print_ascii=False,
         print_fen=False):
    logger.remove(0)
    logger.add(sys.stdout, level=log_level, format='{time:hh:mm:ss.SSS} | <level>{message}</level>')
    board = start_board or chess.Board()
    move = None
    while True:
        if print_svg:
            display(chess.svg.board(board, orientation=orientation, size=300,
                fill=dict.fromkeys(chess.SquareSet([move.from_square, move.to_square]), '#cccc00') if move else {}))
        if print_ascii:
            print(board)
        if print_fen:
            print(board.fen())
        if board.is_game_over():
            break
        move = (whites_player if board.turn == chess.WHITE else blacks_player).choose_move(board)
        board.push(move)

if __name__ == '__main__':
    main()
