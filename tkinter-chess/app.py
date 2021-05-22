# Spencer Burton
# 5/5/2021
# An application class for tkinter

from tkinter import *
from tkinter.font import Font
from PIL import Image, ImageTk
from chess import *
from util import *


class Application(Frame):
    def __init__(self, master, chess_config=DEFAULT_CONFIG):
        super(Application, self).__init__(master)
        self.grid()

        # Board stuff
        self.chess = Chess(chess_config)
        self.tile_imgs = []
        self.tiles = []

        self.is_winner = False

        logo = PhotoImage(file="imgs/logo.png")
        self.master.iconphoto(False, logo)

        self.load_imgs()
        self.create_widgets()
        self.update_visible_board()

    def load_imgs(self):
        blank_img = Image.open("imgs/blank.png")
        blank = ImageTk.PhotoImage(blank_img)
        self.tile_imgs.append(blank)

        for p_type in PIECE_TYPES:
            white_img = Image.open("imgs/white_tiles/white_{}.png".format(p_type))
            black_img = Image.open("imgs/black_tiles/black_{}.png".format(p_type))

            # Convert images
            white = ImageTk.PhotoImage(white_img)
            black = ImageTk.PhotoImage(black_img)

            self.tile_imgs.append(white)
            self.tile_imgs.append(black)

    def create_widgets(self):
        self["bg"] = BG_COLOR

        self.top_label = Label(self, text="Chess", bg=BG_COLOR)
        self.top_label.grid(row=0, column=0, columnspan=9)

        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                bg_color = tile_color_at(x, y)
                tile_index = x + y * BOARD_WIDTH

                button = Button(self, text="e", relief=SUNKEN, bd=0,
                                bg=bg_color, activebackground=bg_color,
                                padx=0, pady=0,
                                image=self.tile_imgs[0], highlightthickness=0,
                                command=lambda i=tile_index: self.tile_click(i))
                button.grid(column=x + 1, row=y + 2, padx=0, pady=0)
                self.tiles.append(button)

        font_style = Font(family="Lucida Grande", size=7)

        for y in range(BOARD_HEIGHT):
            Label(self, text=str(BOARD_HEIGHT - y), bg=BG_COLOR, font=font_style).grid(column=0, row=y + 2, padx=0, pady=0)
            Label(self, text="  ", bg=BG_COLOR, font=font_style).grid(column=BOARD_WIDTH + 1, row=y + 2, padx=0, pady=0)

        for x in range(BOARD_WIDTH):
            Label(self, text=('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')[x], bg=BG_COLOR, font=font_style)\
                .grid(column=x + 1, row=BOARD_HEIGHT + 2, padx=0, pady=0)

    def promote_click(self, new_piece, color, update_command=None, delay=0):
        self.chess.promote(new_piece, color)

        self.bishop_button.grid_remove()
        self.rook_button.grid_remove()
        self.knight_button.grid_remove()
        self.queen_button.grid_remove()

        for tile in self.tiles:
            tile["state"] = "normal"

        self.update_visible_board()

        if update_command is not None:
            self.after(delay, update_command())

    def prompt_promotion(self, color, update_command=None, delay=0):
        self.bishop_button = Button(self, text="Bishop",
                                    command=lambda: self.promote_click("bishop", color, update_command, delay))
        self.bishop_button.grid(column=1, row=5, columnspan=2, rowspan=2)
        self.rook_button = Button(self, text="Rook",
                                  command=lambda: self.promote_click("rook", color, update_command, delay))
        self.rook_button.grid(column=3, row=5, columnspan=2, rowspan=2)
        self.knight_button = Button(self, text="Knight",
                                    command=lambda: self.promote_click("knight", color, update_command, delay))
        self.knight_button.grid(column=5, row=5, columnspan=2, rowspan=2)
        self.queen_button = Button(self, text="Queen",
                                   command=lambda: self.promote_click("queen", color, update_command, delay))
        self.queen_button.grid(column=7, row=5, columnspan=2, rowspan=2)

        for tile in self.tiles:
            tile["state"] = "disabled"

    def tile_click(self, index):
        pass

    def update_visible_board(self, reset_color=True):
        for tile in self.tiles:
            pos = from_index(self.tiles.index(tile))
            piece = self.chess.at(pos)
            tile["image"] = self.tile_imgs[piece_img_index(piece.type, piece.color)]

            if reset_color:
                tile["bg"] = tile_color_at(pos.x, pos.y)

    def check_for_end(self):
        condition, c_or_r = self.chess.check_for_end_condition()

        if condition == "checkmate":
            self.end_game("Checkmate (on {})".format(c_or_r))
            return True
        elif condition == "draw":
            self.end_game("Draw ({})".format(c_or_r))
            return True
        elif condition == "stalemate":
            self.end_game("Stalemate ({} has no moves)".format(c_or_r))
            return True

        return False

    def update_label_text(self, text):
        self.top_label["text"] = text

    def reset_text(self):
        pass

    def end_game(self, message):
        self.reset_button = Button(self, text="New Game", command=lambda: self.reset())
        self.reset_button.grid(row=5, column=4, rowspan=2, columnspan=2)

        for tile in self.tiles:
            tile["state"] = "disabled"

        self.top_label["text"] = message
        self.is_winner = True
        self.update_visible_board()

    def reset(self):
        # Reset all variables
        self.is_winner = False

        for tile in self.tiles:
            tile["state"] = "normal"

        self.reset_button.grid_remove()
        self.chess.reset()
        self.update_visible_board()
        self.update_label_text(self.reset_text())
