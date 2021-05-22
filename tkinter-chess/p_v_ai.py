# Spencer Burton
# 4/5/2021
# Player vs AI

from tkinter import *
from PIL import Image, ImageTk
from ai import *
from app import *


# Application class
class PvAI(Application):
    def __init__(self, master):
        super(PvAI, self).__init__(master)

        # Turn stuff
        self.current_piece = -1
        self.valid_moves = []
        self.ai_player = LeastMovesAI()
        self.black_move_delay = 500
        self.is_winner = False

        # Bind keys for switching ai
        self.master.bind('1', lambda event: self.switch_ai(0))
        self.master.bind('2', lambda event: self.switch_ai(1))
        self.master.bind('3', lambda event: self.switch_ai(2))

        self.update_label_text(self.reset_text())

    def switch_ai(self, ai_type):
        if self.is_winner:
            return

        if ai_type == 0:
            self.ai_player = RandomAI()
        elif ai_type == 1:
            self.ai_player = TakePieceAI()
        elif ai_type == 2:
            self.ai_player = LeastMovesAI()

        self.update_label_text(self.reset_text())

    def tile_click(self, index):
        if self.is_winner:
            return

        # Clear board
        self.update_visible_board()

        curr_pos = from_index(index)

        if self.chess.turn != "white":
            return

        # The user clicked on a valid move
        if curr_pos in self.valid_moves:
            # Do the moves and check for a winner
            self.white_turn(curr_pos)

            # Reset selected piece and valid_moves
            self.valid_moves = []
            self.current_piece = -1

            self.update_visible_board(False)

        # No piece is selected
        else:
            piece = self.chess.at(curr_pos)

            if piece.color == "white":
                self.valid_moves = piece.valid_moves(self.chess.board)

                if FILTER_MOVES_THAT_CHECK:
                    try:
                        self.valid_moves = remove_moves_that_check(self.chess.board, [(piece, self.valid_moves)], "white")[0][1]
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

    def white_turn(self, move):
        piece_pos = self.chess.at(from_index(self.current_piece)).pos
        self.tiles[piece_pos.index()]["bg"] = move_color_at(piece_pos.x, piece_pos.y)
        self.chess.attempt_move(piece_pos, move)

        if self.check_for_end():
            return

        if self.chess.has_promotion() == "white":
            self.prompt_promotion("white", self.black_turn, self.black_move_delay)
        else:
            self.after(self.black_move_delay, self.black_turn)

    def black_turn(self):
        black_move_info = self.ai_player.choose_move(self.chess.board, "black")

        if black_move_info is None:
            self.check_for_end()
            return

        black_piece = black_move_info[0]
        black_move = black_move_info[1]
        # Show where the piece moved from
        move_color = move_color_at(black_piece.pos.x, black_piece.pos.y)
        old_pos = black_piece.pos.index()
        self.chess.attempt_move(black_piece.pos, black_move)

        self.update_visible_board()
        self.tiles[old_pos]["bg"] = move_color

        if self.check_for_end():
            return

    def reset_text(self):
        return "Chess : {}".format(self.ai_player.name)


def main():
    root = Tk()
    root.title("Chess: P vs AI")
    root.geometry("{}x{}".format(WIDTH, HEIGHT))
    root.resizable(0, 0)

    PvAI(root)

    root.mainloop()


main()
