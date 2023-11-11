import chess
import chess.svg
from IPython.display import display

class HumanPlayer:
    def choose_move(self, board):
        while True:
            print('Enter your move (SAN):')
            try:
                move = board.parse_san(input())
                return move
            except KeyboardInterrupt:
                raise
            except:
                print('Failed to parse')