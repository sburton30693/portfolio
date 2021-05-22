# Spencer Burton
# 4/5/2021
# Testing

from ai import *
from app import *

config = \
    "+kq======"\
    " pppppppp"\
    " ========"\
    " ========"\
    " ========"\
    " ========"\
    "-pppppppp"\
    " ====k==r"


# Application class
class Test(Application):
    def __init__(self, master):
        super(Test, self).__init__(master, config)

        # Turn stuff
        self.current_piece = -1
        self.valid_moves = []
        self.ai_player = LeastMovesAI()
        self.is_winner = False

        self.update_label_text("Chess : {}'s Turn".format(self.chess.turn))

    def tile_click(self, index):
        if self.is_winner:
            return

        # Clear board
        self.update_visible_board()

        curr_pos = from_index(index)

        # The user clicked on a valid move
        if curr_pos in self.valid_moves:
            # Get the current piece
            piece_pos = curr_pos
            piece = self.chess.at(piece_pos)

            # Do the moves and check for a winner
            self.do_turn(curr_pos, self.chess.turn)

            # Reset selected piece and valid_moves
            self.valid_moves = []
            self.current_piece = -1

            self.update_visible_board(False)

        # No piece is selected
        else:
            piece = self.chess.at(curr_pos)

            if piece.color == self.chess.turn:
                self.valid_moves = piece.valid_moves(self.chess.board)

                if FILTER_MOVES_THAT_CHECK:
                    try:
                        self.valid_moves = \
                            remove_moves_that_check(self.chess.board, [(piece, self.valid_moves)], self.chess.turn)[0][1]
                    except IndexError:
                        self.valid_moves = []
                        self.current_piece = -1
                        return

                self.current_piece = index

                # Highlight valid moves
                for move in self.valid_moves:
                    color = move_color_at(move.x, move.y)
                    self.tiles[move.index()]["bg"] = color
            else:
                self.valid_moves = []
                self.current_piece = -1

    def do_turn(self, move, color):
        piece_pos = self.chess.at(from_index(self.current_piece)).pos
        self.tiles[piece_pos.index()]["bg"] = move_color_at(piece_pos.x, piece_pos.y)
        self.chess.attempt_move(piece_pos, move)

        if self.check_for_end():
            return

        if self.chess.has_promotion() == color:
            self.prompt_promotion(color)

        self.update_label_text("Chess : {}'s Turn".format(self.chess.turn))

    def reset_text(self):
        return "Chess : {}'s Turn".format(self.chess.turn)


def main():
    root = Tk()
    root.title("Chess")
    root.geometry("{}x{}".format(WIDTH, HEIGHT))
    root.resizable(0, 0)

    Test(root)

    root.mainloop()


main()
