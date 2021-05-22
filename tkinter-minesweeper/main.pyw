# 2/18/2021

import random 
from tkinter import Tk, Frame, Button, Label, Menu

BOARD_WIDTH = 16
BOARD_HEIGHT = 16

TILE_MINE = 0
TILE_EMPTY = 1

NUM_TILES = BOARD_WIDTH * BOARD_HEIGHT
NUM_MINES = 30

CHECKER_GREEN_DARK  = "#57f781"
CHECKER_GREEN_LIGHT = "#24a647"
CHECKER_GREY_DARK  = "#c9c9c9"
CHECKER_GREY_LIGHT = "#d1d1d1"
MINE_COLOR = "#3657ff"

FLAG_CHAR = "⚑"


def xy_to_index(x, y):
    return x + y * BOARD_WIDTH

def coords_to_index(coords):
    return coords[0] + coords[1] * BOARD_WIDTH

def index_to_coords(index):
    return (index % BOARD_WIDTH, index // BOARD_WIDTH)

def checker_color(index, color1, color2):
    if (index + index // BOARD_WIDTH) % 2:
        return color1
    else:
        return color2

def index_oob(index):
    coords = index_to_coords(index)
    
    if coords[0] < 0 or coords[0] >= BOARD_WIDTH or coords[1] < 0 or coords[1] >= BOARD_HEIGHT:
        return True

    return False


class Queue(object):
    def __init__(self):
        self.array = []
        self.size = 0

    def push(self, object):
        self.array.append(object)
        self.size += 1

    def pop(self):
        if self.size <= 0:
            return None

        self.size -= 1
        return self.array.pop(0)


class Tile(object):
    def __init__(self, tile_type=TILE_EMPTY, num_mines=0, revealed=False):
        self.type = tile_type
        self.mines_around = num_mines
        self.flags_around = 0
        self.revealed = revealed
        self.flagged = False

    def is_blank(self):
        return self.type == TILE_EMPTY and self.mines_around == 0

    def is_revealed(self):
        return self.revealed

    def is_flagged(self):
        return self.flagged


class MineSweeper(Frame):
    def __init__(self, master):
        super(MineSweeper, self).__init__(master)
        self.tiles = []
        self.mines_left = NUM_MINES
        self.tiles_left = NUM_TILES
        self.gameover = False
        self.show_stats = False
        self.show_stat_nums = False
        self.grid()
        self.top_lbl = Label(self, text="Mines: " + str(NUM_MINES))
        self.top_lbl.grid(row=0, columnspan=BOARD_WIDTH)
        self.create_tiles()
        self.create_menubar()
        self.place_mines()
        self.generate_tiles()

    def create_menubar(self):
        menubar = Menu(self)
        self.master.config(menu=menubar)

        game = Menu(menubar, tearoff=False)
        game.add_command(label="New Game", command=self.new_game)
        menubar.add_cascade(label="Game", menu=game)

        options = Menu(menubar, tearoff=False)
        options.add_command(label="Toggle Statistics", command=self.toggle_statistics)
        options.add_command(label="Toggle Tile Numbers", command=self.toggle_stat_numbers)
        menubar.add_cascade(label="Options", menu=options)

        debug = Menu(menubar, tearoff=False)
        debug.add_command(label="Clear All", command=self.clear_all)
        debug.add_command(label="Reset All", command=self.reset_all)
        menubar.add_cascade(label="Debug", menu=debug)

    def create_tiles(self):
        color = ""
        for i in range(NUM_TILES):
            color = checker_color(i, CHECKER_GREEN_DARK, CHECKER_GREEN_LIGHT)

            self.tiles.append((Tile(),
                Button(self, highlightcolor="white", bd=1, bg=color, activebackground=color, relief="flat", font="Calibra 10", width=2, height=1, command=lambda i=i: self.on_left_click(i))))
            self.tiles[i][1].grid(row=(i // BOARD_WIDTH) + 1, column=i % BOARD_WIDTH)
            self.tiles[i][1].bind("<Button-2>", self.on_right_click)
            self.tiles[i][1].bind("<Button-3>", self.on_right_click)

    def print_coords_debug(self, event):
        """This is a debug function used for testing and was bound to the middle mouse button"""
        index = 0
        for i in range(NUM_TILES):
            tile = self.tiles[i]
            if tile[1] == event.widget:
                index = i
        
        coords = index_to_coords(index)
        print(str.format("Tile at ({}, {}), Blank: {}", coords[0], coords[1], self.tiles[index][0].is_blank()))

    def on_right_click(self, event):
        """Ran when the tile is clicked with the right or middle mouse button"""
        if self.gameover:
            return

        if self.check_win():
            self.win()
            return

        # This is annoying to do, I probably should have structured this better
        index = 0
        for i in range(NUM_TILES):
            tile = self.tiles[i]
            if tile[1] == event.widget:
                index = i
        
        tile = self.tiles[index]

        if tile[0].is_revealed():
            return

        if tile[0].is_flagged():
            tile[1].config(text="", state="normal")
            tile[0].flagged = False
            self.mines_left += 1
        else:
            tile[1].config(text=FLAG_CHAR, state="disabled")
            tile[0].flagged = True
            self.mines_left -= 1

        coords = index_to_coords(index)
        outer_tiles = self.get_outer_tiles(coords[0], coords[1])
        for outer_tile in outer_tiles:
            if tile[0].is_flagged():
                outer_tile[0].flags_around += 1
            else:
                outer_tile[0].flags_around -= 1

        self.update_label()

        if self.show_stats:
            self.update_statistics()

    def on_left_click(self, index):
        """Ran when the tile's button is clicked with the left mouse button"""
        if self.tiles[index][0].is_flagged():
            return

        # Check for mine first
        if self.tiles[index][0].type == TILE_MINE:
            self.game_over()
            return

        if self.tiles[index][0].is_blank():
            self.flood_clear(index)
        else:
            self.clear_tile(index)

        if self.show_stats:
            self.update_statistics()

        if self.check_win():
            self.win()
            return

    def game_over(self):
        """Does some stuff to signal that the game is over because a mine was clicked"""
        # Reveal all mines and disable all tiles
        for i in range(NUM_TILES):
            tile = self.tiles[i]
            if tile[0].type == TILE_MINE:
                tile[1].config(bg=MINE_COLOR)
            
            tile[1].config(state="disable")

        # Set the label's text to Game Over
        self.top_lbl.config(text="GAME OVER")
        self.gameover = True

    def check_win(self):
        """Check for a win and display a little message and disable all tiles if so"""
        for i in range(NUM_TILES):
            tile = self.tiles[i]

            if (tile[0].type == TILE_MINE and tile[0].is_revealed()) or (tile[0].type == TILE_EMPTY and not tile[0].is_revealed()):
                return False

        return True 

    def win(self):
        # Use the stuff from the game_over method but change the label
        self.game_over()
        self.top_lbl.config(text="YOU WON!")

    def new_game(self):
        """Resets all the game variables, and places new mines"""
        for i in range(NUM_TILES):
            self.tiles[i][0].type = TILE_EMPTY
            self.tiles[i][0].mines_around = 0
            self.tiles[i][0].flagged = False

        self.place_mines()
        self.generate_tiles()
        self.reset_all()

    def clear_tile(self, index):
        """Changes the background and disables the button, reveals it"""
        bg = checker_color(index, CHECKER_GREY_DARK, CHECKER_GREY_LIGHT)
        text = ""
        tile = self.tiles[index]

        if self.tiles[index][0].mines_around != 0:
            text = str(self.tiles[index][0].mines_around)
        elif self.tiles[index][0].type == TILE_MINE:
            bg = MINE_COLOR

        tile[1].config(bg=bg, text=text, state="disabled")
        tile[0].revealed = True
        self.tiles_left -= 1

        if tile[0].is_flagged():
            tile[0].flagged = False
            self.mines_left += 1
            self.update_label()

    def flood_clear(self, index):
        if self.tiles[index][0].is_blank():
            coords = index_to_coords(index)
            queue = Queue()
            queue.push(coords)

            while queue.size > 0:
                tile_coords = queue.pop()
                tile = self.get_tile(tile_coords[0], tile_coords[1])
                self.clear_tile(coords_to_index(tile_coords))

                if tile.is_blank():
                    outer_tiles = self.get_outer_tiles(tile_coords[0], tile_coords[1])

                    for outer_tile in outer_tiles:
                        x = outer_tile[1][0]
                        y = outer_tile[1][1]

                        if x < 0 or x >= BOARD_WIDTH or y < 0 or y >= BOARD_HEIGHT:
                            continue

                        if outer_tile[0].type == TILE_EMPTY and not outer_tile[0].is_revealed() and outer_tile[1] not in queue.array:
                            queue.push(outer_tile[1])

    def clear_all(self):
        """Clears every single tile, for debug purposes only"""
        for i in range(NUM_TILES):
            self.clear_tile(i)

    def reset_all(self):
        """Resets tiles and stuff"""
        for i in range(NUM_TILES):

            self.tiles[i][1].config(bg=checker_color(i, CHECKER_GREEN_DARK, CHECKER_GREEN_LIGHT), text="", state="normal")
            self.tiles[i][0].revealed = False

        self.mines_left = NUM_MINES
        self.tiles_left = NUM_TILES
        self.update_label()
        self.gameover = False

        if self.show_stats:
            self.update_statistics()

    def update_label(self):
        """Update the label at the top, which contains information about mines and stuff"""
        self.top_lbl.config(text="Mines: " + str(self.mines_left))

    def toggle_statistics(self):
        self.show_stats = not self.show_stats
        
        if self.show_stats:
            self.update_statistics()
        else:
            self.remove_statistics()

    def toggle_stat_numbers(self):
        self.show_stat_nums = not self.show_stat_nums

        if self.show_stats:
            # Remove in order to get rid of the numbers
            self.remove_statistics()
            self.update_statistics()

    def update_statistics(self):
        if self.gameover:
            return

        for i in range(NUM_TILES):
            tile = self.tiles[i]

            if not tile[0].is_revealed():
                coords = index_to_coords(i)
                outer_tiles = self.get_outer_tiles(coords[0], coords[1])
                ratio = 0
                empty_neighboors = True

                for outer_tile in outer_tiles:
                    if outer_tile[0].is_revealed():
                        empty_neighboors = False
                        possible_mines = outer_tile[0].mines_around - outer_tile[0].flags_around
                        ratio += possible_mines > 0

                if empty_neighboors:
                    ratio = int(8 * (self.mines_left / self.tiles_left))

                color = str.format("#{:02x}0000", int((ratio + 2) / 10 * 255))
                tile[1].config(bg=color, activebackground=color)

                if self.show_stat_nums and tile[1]["text"] != FLAG_CHAR:
                    tile[1].config(text=str(ratio))

    def remove_statistics(self):
        for i in range(NUM_TILES):
            if not self.tiles[i][0].is_revealed():
                color = checker_color(i, CHECKER_GREEN_DARK, CHECKER_GREEN_LIGHT)
                self.tiles[i][1].config(bg=color, activebackground=color)

                if self.tiles[i][1]["text"] != FLAG_CHAR:
                    self.tiles[i][1].config(text="")



    def place_mines(self):
        """Put mines in random spots"""
        mine_spots = []
        for i in range(NUM_MINES):
            index = random.randint(0, NUM_TILES - 1)
            while index in mine_spots:
                index = random.randint(0, NUM_TILES - 1)

            mine_spots.append(index)
            self.tiles[index][0].type = TILE_MINE

    def generate_tiles(self):
        """Put the correct number into a tile"""
        for i in range(NUM_TILES):
            if self.tiles[i][0].type != TILE_MINE:
                coords = index_to_coords(i)
                
                # Get 8 tiles around it
                outer_tiles = self.get_outer_tiles(coords[0], coords[1])

                num_mines = 0
                for j in range(8):
                    if outer_tiles[j][0].type == TILE_MINE:
                        num_mines += 1

                self.tiles[i][0].mines_around = num_mines

    def get_outer_tiles(self, x, y):
        tile_nw = self.get_tile(x - 1, y - 1)
        tile_n  = self.get_tile(x,     y - 1)
        tile_ne = self.get_tile(x + 1, y - 1)
        tile_w  = self.get_tile(x - 1, y)
        tile_e  = self.get_tile(x + 1, y)
        tile_sw = self.get_tile(x - 1, y + 1)
        tile_s  = self.get_tile(x    , y + 1)
        tile_se = self.get_tile(x + 1, y + 1)
        outer_tiles = [(tile_nw, (x - 1, y - 1)), (tile_n, (x, y - 1)), (tile_ne, (x + 1, y - 1)), (tile_w, (x - 1, y)), 
                       (tile_e , (x + 1, y)), (tile_sw, (x - 1, y + 1)), (tile_s, (x, y + 1)), (tile_se, (x + 1, y + 1))]
        
        return outer_tiles

    def get_tile(self, x, y):
        index = xy_to_index(x, y)

        if x < 0 or x >= BOARD_WIDTH or y < 0 or y >= BOARD_HEIGHT:
            # Return empty tile if index out of range
            return Tile()

        elif index in range(NUM_TILES):
            return self.tiles[index][0]


def main():
    root = Tk()
    root.title("MineSweeping my dude")
    root.resizable(0, 0)
    MineSweeper(root)

    root.mainloop()


main()
