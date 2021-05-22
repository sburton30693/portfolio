# Imports
import pygame as pg
import random
import os

# Setup folder Assets
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "imgs")
snd_folder = os.path.join(game_folder, "snds")
level_folder = os.path.join(game_folder, "levels")

# Constants
TITLE = "Tile-Based Game"

WIDTH = 1024
HEIGHT = 768
FPS = 60
FONT_NAME = pg.font.match_font("arial")

TILE_SIZE = 32
GRID_WIDTH = WIDTH / TILE_SIZE
GRID_HEIGHT = WIDTH / TILE_SIZE
NUM_LEVELS = 4

PLAYER_ACC = 0.25
PLAYER_GRAV = 0.05
PLAYER_MAX_VEL = 50
PLAYER_TURN_SPEED = 2.5
LANDING_SPEED_MAX = 15

# Colors (R, G, B)
BLACK = (0, 0, 0)
ALMOST_BLACK = (1, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
LIGHT_GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PINK = (255, 125, 220)
PURPLE = (153, 0, 255)
LIME = (100, 255, 0)