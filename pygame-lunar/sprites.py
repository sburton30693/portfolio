# Imports
import pygame as pg
from settings import *
import math

vec = pg.math.Vector2


def sign(value):
    if value < 0:
        return -1
    elif value > 0:
        return 1
    else:
        return 0


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        super(Player, self).__init__(self.groups)
        self.game = game
        self.off_image = self.game.ship_off_img
        self.off_image.set_colorkey(BLACK)
        self.on_image = self.game.ship_on_img
        self.on_image.set_colorkey(BLACK)
        self.image = self.off_image
        self.rect = self.image.get_rect()
        self.pos = vec(x * TILE_SIZE + self.rect.width / 2, y * TILE_SIZE + self.rect.height / 2)
        self.rect.topleft = (self.pos.x, self.pos.y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.landed = False
        self.dir = vec(0, 1)
        self.deg = 90
        self.on = False
        self.fuel = 1000

    def update(self):
        self.get_keys()

        if not self.landed:
            self.pos += (self.vel + 0.5 * self.acc) * self.game.dt
            self.rect.center = (self.pos.x, self.pos.y)
            self.collide_with_walls()

    def rotate_img(self):
        if self.on:
            self.image = pg.transform.rotate(self.on_image, self.deg - 90)
        else:
            self.image = pg.transform.rotate(self.off_image, self.deg - 90)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos.x, self.pos.y)

    def collide_with_walls(self):
        hits = pg.sprite.spritecollide(self, self.game.walls, False)
        if hits:
            hits = pg.sprite.spritecollide(self, self.game.walls, False, pg.sprite.collide_mask)
            if hits:
                for hit in hits:
                    if hit.type != "f":
                        self.game.playing = False
                    else:
                        if self.vel.y > LANDING_SPEED_MAX:
                            self.game.playing = False
                        else:
                            self.landed = True

                            if self.game.level == 3:
                                self.game.win = True

    def get_keys(self):
        self.acc = vec(0, PLAYER_GRAV)

        keys = pg.key.get_pressed()

        if self.landed:
            if keys[pg.K_RETURN]:
                self.game.level += 1
                self.game.playing = False

                if self.game.win:
                    self.game.level = 0
        else:
            if keys[pg.K_LEFT]:
                self.deg += PLAYER_TURN_SPEED
            if keys[pg.K_RIGHT]:
                self.deg -= PLAYER_TURN_SPEED

            self.rotate_img()
            self.dir = vec(-math.cos(math.radians(self.deg)), math.sin(math.radians(self.deg)))

            if keys[pg.K_SPACE]:
                self.acc += -PLAYER_ACC * self.dir
                self.on = True
                self.fuel -= 0.75
            else:
                self.on = False

            if self.fuel <= 0:
                self.game.playing = False

            self.vel += self.acc
            if abs(self.vel.x) > PLAYER_MAX_VEL:
                self.vel.x = PLAYER_MAX_VEL * sign(self.vel.x)
            if abs(self.vel.y) > PLAYER_MAX_VEL:
                self.vel.y = PLAYER_MAX_VEL * sign(self.vel.y)


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y, img, flip, type, colorkey):
        self.groups = game.all_sprites, game.walls
        super(Wall, self).__init__(self.groups)
        self.game = game
        self.image = img.copy()
        if flip:
            self.image = pg.transform.flip(img, True, False)
        self.image.set_colorkey(colorkey)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE
        self.type = type
