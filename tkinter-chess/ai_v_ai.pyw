# Spencer Burton
# 4/5/2021
# AI vs AI

from ai import *
from app import *


# Application class
class AIvAI(Application):
    def __init__(self, master):
        super(AIvAI, self).__init__(master)
        # AI Players
        self.ai_player1 = RandomAI()
        self.ai_player2 = LeastMovesAI()

        self.start = False
        self.delay = 50

        # Buttons for switching the AI
        self.master.bind('1', lambda event: self.switch_ai_1(0))
        self.master.bind('2', lambda event: self.switch_ai_1(1))
        self.master.bind('3', lambda event: self.switch_ai_1(2))
        self.master.bind('4', lambda event: self.switch_ai_2(0))
        self.master.bind('5', lambda event: self.switch_ai_2(1))
        self.master.bind('6', lambda event: self.switch_ai_2(2))

        self.update_label_text(self.reset_text())

    def switch_ai_1(self, ai_type):
        if self.start:
            return

        if ai_type == 0:
            self.ai_player1 = RandomAI()
        elif ai_type == 1:
            self.ai_player1 = TakePieceAI()
        elif ai_type == 2:
            self.ai_player1 = LeastMovesAI()

        self.update_label_text(self.reset_text())

    def switch_ai_2(self, ai_type):
        if self.start:
            return

        if ai_type == 0:
            self.ai_player2 = RandomAI()
        elif ai_type == 1:
            self.ai_player2 = TakePieceAI()
        elif ai_type == 2:
            self.ai_player2 = LeastMovesAI()

        self.update_label_text(self.reset_text())

    def tile_click(self, index):
        if not self.start:
            self.start = True
            self.do_move()

    def do_move(self):
        self.update_visible_board()

        if self.chess.turn == "white":
            move = self.ai_player1.choose_move(self.chess.board, self.chess.turn)
        else:
            move = self.ai_player2.choose_move(self.chess.board, self.chess.turn)

        if move is None:
            self.check_for_end()
            self.start = False
            return

        self.tiles[move[0].pos.index()]["bg"] = move_color_at(move[0].pos.x, move[0].pos.y)
        self.chess.attempt_move(move[0].pos, move[1])
        self.update_visible_board(False)

        promote = self.chess.has_promotion()
        if promote:
            self.chess.promote("queen", promote)

        if self.check_for_end():
            self.start = False
            return

        self.after(self.delay, self.do_move)

    def reset_text(self):
        return "Chess:  White: {}, Black: {}".format(self.ai_player1.name, self.ai_player2.name)


def main():
    root = Tk()
    root.title("Chess: AI vs AI")
    root.geometry("{}x{}".format(WIDTH, HEIGHT))
    root.resizable(0, 0)

    AIvAI(root)

    root.mainloop()


main()
