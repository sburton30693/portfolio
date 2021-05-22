# Spencer Burton
# 4/5/2021
# New Pygame Template

# Imports
import pygame as pg
import random
from settings import *
from os import path
from sprites import *


def draw_text(surface, text, size, x, y, color=WHITE):
    font = pg.font.Font(FONT_NAME, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)


class Game(object):
    def __init__(self):
        self.running = True
        self.level = 0
        self.win = False

        # Initialize PyGame and create a window
        pg.init()
        pg.mixer.init()

        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.load_data()

    def load_data(self):
        self.levels = []
        for i in range(NUM_LEVELS):
            with open(path.join(level_folder, "level_{}.txt".format(i)), "rt") as f:
                map_data = []
                for line in f:
                    map_data.append(line)
                self.levels.append(map_data)

        self.burn_img = pg.image.load(path.join(img_folder, "Fire.png"))
        self.ship_off_img = pg.image.load(path.join(img_folder, "Ship_off.png"))
        self.ship_on_img = pg.image.load(path.join(img_folder, "Ship_on.png"))

        self.floor_imgs = []
        self.floor_imgs.append(pg.image.load(path.join(img_folder, "F0.png")))
        self.floor_imgs.append(pg.image.load(path.join(img_folder, "F1-0.png")))
        self.floor_imgs.append(pg.image.load(path.join(img_folder, "F1-1.png")))
        self.floor_imgs.append(pg.image.load(path.join(img_folder, "F3-0.png")))
        self.floor_imgs.append(pg.image.load(path.join(img_folder, "F3-1.png")))
        self.floor_imgs.append(pg.image.load(path.join(img_folder, "F2.png")))
        self.floor_imgs.append(pg.image.load(path.join(img_folder, "F4.png")))

        self.background = pg.image.load(path.join(img_folder, "Earth.jpg"))

        pg.mixer.music.load(path.join(snd_folder, "lacrimosa-stretched.ogg"))
        pg.mixer.music.play(-1)


    def new_game(self):
        """start a new game"""
        # create sprite groups
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()

        # create game objects
        colorkey = BLACK
        for row, tiles in enumerate(self.levels[self.level]):
            offset = 0
            for col, tile in enumerate(tiles):
                if tile == "P":
                    self.player = Player(self, col - offset, row)
                elif tile == "f":
                    Wall(self, col - offset, row, self.floor_imgs[5], False, tile, colorkey)
                elif tile == "a":
                    Wall(self, col - offset, row, self.floor_imgs[6], False, tile, BLACK)
                elif tile in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
                    Wall(self, col - offset, row, self.floor_imgs[int(tile) // 2], int(tile) % 2 != 0, tile, colorkey)
                elif tile == "-":
                    colorkey = ALMOST_BLACK
                    offset += 1
                elif tile == "+":
                    colorkey = BLACK
                    offset += 1

        self.run()

    def run(self):
        self.playing = True

        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000

            self.events()
            self.update()
            self.draw()

    def events(self):
        # Process Input
        for event in pg.event.get():
            # Check for closing window
            if event.type == pg.QUIT:
                self.quit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.background, (-700, 75))
        self.all_sprites.draw(self.screen)

        draw_text(self.screen, "Fuel: {:.1f}".format(self.player.fuel / 10), 20, 50, 10)
        draw_text(self.screen, "Level: {}".format(self.level + 1), 20, 50, 30)

        if self.player.landed:
            if not self.win:
                draw_text(self.screen, "Press Enter to continue", 40, WIDTH / 2, HEIGHT / 2)
            else:
                draw_text(self.screen, "Congratulations!", 40, WIDTH / 2, HEIGHT / 2)

        pg.display.flip()

    def show_start_screen(self):
        self.screen.blit(self.background, (-700, 75))
        draw_text(self.screen, "Lunar Lander", 12, WIDTH / 2, HEIGHT / 4)
        draw_text(self.screen, "in", 8, WIDTH / 2, HEIGHT / 4 + 14)
        draw_text(self.screen, "Landing of the Lunar Lander", 40, WIDTH / 2, HEIGHT / 4 + 24, GRAY)
        draw_text(self.screen, "How to Play:", 15, WIDTH / 2, HEIGHT * 3 / 4)
        draw_text(self.screen, "Hold the space bar to propel the lander in the direction it's facing.", 15, WIDTH / 2, HEIGHT * 3 / 4 + 20)
        draw_text(self.screen, "Land safetly on the ground marked 'F' in order to progress.", 15, WIDTH / 2, HEIGHT * 3 / 4 + 34)
        draw_text(self.screen, "Press any key to continue", 15, WIDTH / 2, HEIGHT * 3 / 4 + 48)
        pg.display.flip()

        waiting = True
        while waiting:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    waiting = False

                if event.type == pg.KEYDOWN:
                    waiting = False

    def quit(self):
        self.playing = False
        self.running = False


g = Game()
g.show_start_screen()

while g.running:
    g.new_game()

pg.quit()
