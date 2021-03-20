# Spencer Burton
# 3/5/2021

# Attributions ############################################
# Code and Ship art by Spencer Burton
# Bullet and Meteor Art by "kenny.nl" or "www.kenny.nl"
# Background by Unknown Photographer
# Bullet Sound by dklon

# Imports #################################################
import pygame as pg
import random as r
import math
from os import *


# Game Object Classes ####################################

class Star(pg.sprite.Sprite):
    def __init__(self):
        super(Star, self).__init__()
        self.size = r.randint(1, 4)
        self.image = pg.Surface((self.size, self.size))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (r.randint(0, WIDTH), r.randint(0, HEIGHT))
        self.speed = r.choice((14, 15))

    def update(self):
        self.rect.y += self.speed

        if self.rect.top >= HEIGHT:
            self.rect.centerx = r.randint(0, WIDTH)
            self.rect.bottom = 0


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, size=5):
        super(Bullet, self).__init__()
        # self.image = pg.Surface((size, 20))
        # self.image.fill(BLUE)
        self.image = pg.transform.scale(bullet_img, (int(size), 20))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed = -20

    def update(self):
        self.rect.y += self.speed

        # Kill bullet when it goes off the top of the screen
        if self.rect.bottom <= 0:
            self.kill()


class Player(pg.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        # self.image = pg.Surface((50, 40))
        # self.image.fill(GREEN)
        self.health = 100
        self.size = (60, 45)
        self.image = pg.transform.scale(player_img, self.size)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 23
        self.rect.centerx = WIDTH/2
        self.rect.bottom = (HEIGHT - (HEIGHT * 0.1))
        self.speedx = 0
        self.speed_num = 7
        self.base_size = 5
        self.bullet_size = self.base_size
        self.left_image = False
        self.right_image = False
        self.last_shot = pg.time.get_ticks()
        self.base_delay = 250
        self.shot_delay = self.base_delay
        self.power = ""
        self.power_length = 0
        self.power_color = BLACK

    def update(self):
        key_states = pg.key.get_pressed()
        self.speedx = 0

        if key_states[pg.K_RIGHT] or key_states[pg.K_d]:
            self.speedx += self.speed_num
            if not self.right_image:
                self.right_image = True
                self.left_image = False
                self.image = pg.transform.scale(player_right_img, self.size)
                self.image.set_colorkey(BLACK)
        elif key_states[pg.K_LEFT] or key_states[pg.K_a]:
            self.speedx += -self.speed_num
            if not self.left_image:
                self.left_image = True
                self.right_image = False
                self.image = pg.transform.scale(player_left_img, self.size)
                self.image.set_colorkey(BLACK)
        elif self.left_image or self.right_image:
            self.image = pg.transform.scale(player_img, self.size)
            self.image.set_colorkey(BLACK)
            self.left_image = False
            self.right_image = False

        if self.power_length > 0:
            if self.power == "Rapid Fire":
                self.bullet_size = self.base_size
                self.shot_delay = 50
            elif self.power == "Big Bullets":
                self.shot_delay = self.base_delay
                self.bullet_size = 50
            elif self.power == "Laser Fire":
                self.bullet_size = self.base_size
                self.shot_delay = 0

            self.power_length -= 1
        else:
            self.shot_delay = self.base_delay
            self.bullet_size = self.base_size

        if key_states[pg.K_DOWN]:
            self.shot_delay -= 1
        if key_states[pg.K_UP]:
            self.shot_delay += 1

        # Fire a bullet if holding space
        if key_states[pg.K_SPACE]:
            self.shoot_dual()

        self.rect.x += self.speedx

        # Keep from leaving the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def shoot(self):
        now = pg.time.get_ticks()

        if now - self.last_shot >= self.shot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top - 1, self.bullet_size)
            bullet_group.add(bullet)
            all_sprites.add(bullet)
            pew_sound.play(maxtime=100)

    def shoot_dual(self):
        now = pg.time.get_ticks()

        if now - self.last_shot >= self.shot_delay:
            self.last_shot = now
            bulletl = Bullet(self.rect.left, self.rect.top - 1, self.bullet_size)
            bulletr = Bullet(self.rect.right, self.rect.top - 1, self.bullet_size)
            bullet_group.add(bulletl)
            bullet_group.add(bulletr)
            all_sprites.add(bulletl)
            all_sprites.add(bulletr)
            pew_sound.play(maxtime=100)


class PowerUp(pg.sprite.Sprite):
    def __init__(self, type, color):
        super(PowerUp, self).__init__()
        self.image = pg.Surface((25, 25))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 25 / 2
        self.color = color
        pg.draw.circle(self.image, color, self.rect.center, self.radius)
        self.rect.x = r.randint(0, WIDTH)
        self.rect.bottom = 0
        self.type = type

    def update(self):
        self.rect.y += 5

        if self.rect.top >= HEIGHT:
            self.kill()


class NPC(pg.sprite.Sprite):
    def __init__(self):
        super(NPC, self).__init__()
        # self.image = pg.Surface((25, 25))
        # self.image.fill(RED)
        self.image = enemy_img
        self.size = r.randint(25, 50)
        self.image_orig = pg.transform.scale(enemy_img, (self.size, self.size))
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.new_image = self.image
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width/2 * 0.75)
        #pg.draw.circle(self.image_orig, RED, self.rect.center, self.radius)
        self.rect.centerx = r.randint(0, WIDTH)
        self.rect.bottom = 0
        self.speed = [r.random() * 10 - 5, r.random() * 15 + 5]
        self.rot = 0
        self.rot_speed = r.randint(-8, 8)
        self.last_update = pg.time.get_ticks()

    def rotate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 60:
            last_update = now
            # Do the rotation
            self.rot = (self.rot + self.rot_speed) % 360
            self.image = pg.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()

        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]

        if self.rect.top > HEIGHT:
            self.rect.centerx = r.randint(0, WIDTH)
            self.rect.bottom = 0
            self.speed = [r.random() * 10 - 5, r.random() * 5 + 5]

        if self.rect.bottom < 0:
            self.kill()

    def spawn(self):
        new_npc = NPC()
        npc_group.add(new_npc)
        all_sprites.add(new_npc)


# Game Constants #########################################
WIDTH = 600
HEIGHT = 900
FPS = 60

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PINK = (255, 125, 220)
PURPLE = (153, 0, 255)
LIME = (100, 255, 0)

title = "Shmup"
font_name = pg.font.match_font("arial")

# Folders
game_folder = path.dirname(__file__)
imgs_folder = path.join(game_folder, "imgs")
scores_folder = path.join(game_folder, "scores")
snds_folder = path.join(game_folder, "snds")
player_img_folder = path.join(imgs_folder, "player")
enemy_img_folder = path.join(imgs_folder, "enemy")
background_img_folder = path.join(imgs_folder, "backgrounds")

# Game Functions ##########################################
def draw_text(surface, text, size, color, x, y):
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)


def draw_bar(surface, x, y, color, pct):
    if pct < 0:
        pct = 0

    bar_len = 200
    bar_height = 15
    fill = (pct / 100) * bar_len
    outline_rect = pg.Rect(x, y, bar_len, bar_height)
    fill_rect = pg.Rect(x, y, fill, bar_height)

    pg.draw.rect(surface, color, fill_rect)
    pg.draw.rect(surface, WHITE, outline_rect, 3)


def new_power():
    type = r.choice(["Rapid Fire", "Big Bullets", "Laser Fire"])
    if type == "Rapid Fire":
        color = YELLOW
    elif type == "Big Bullets":
        color = BLUE
    elif type == "Laser Fire":
        color = PURPLE

    power = PowerUp(type, color)
    return power

# Initialize Pygame #######################################
pg.init()
pg.mixer.init()

screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption(title)
clock = pg.time.Clock()


# Load Images #############################################
background = pg.image.load(path.join(background_img_folder, "galaxy.jpg")).convert()
background = pg.transform.scale(background, (WIDTH, HEIGHT))
background_rect = background.get_rect()

player_img = pg.image.load(path.join(player_img_folder, "ship.png")).convert()
player_right_img = pg.image.load(path.join(player_img_folder, "ship_right_turn.png")).convert()
player_left_img = pg.image.load(path.join(player_img_folder, "ship_left_turn.png")).convert()

enemy_img = pg.image.load(path.join(enemy_img_folder, "meteor.png")).convert()

bullet_img = pg.image.load(path.join(player_img_folder, "laser.png")).convert()

# Load Sounds #############################################
pew_sound = pg.mixer.Sound(path.join(snds_folder, "pewpew_1.wav"))
expl_1 = pg.mixer.Sound(path.join(snds_folder, "expl3.wav"))
expl_2 = pg.mixer.Sound(path.join(snds_folder, "expl6.wav"))
expl_sounds = [expl_1, expl_2]

pg.mixer.music.load(path.join(snds_folder, "tgfcoder-FrozenJam.ogg"))
pg.mixer.music.set_volume(0.1)
pg.mixer.music.play(loops=-1)

# Create Sprite Groups ####################################
all_sprites = pg.sprite.Group()
player_group = pg.sprite.Group()
npc_group = pg.sprite.Group()
star_group = pg.sprite.Group()
power_group = pg.sprite.Group()
bullet_group = pg.sprite.Group()

# Create Game Objects #####################################
player = Player()

for i in range(20):
    npc = NPC()
    npc_group.add(npc)

for i in range(50):
    star = Star()
    star_group.add(star)

# Add Objects to Sprite Groups ############################
player_group.add(player)

for i in player_group:
    all_sprites.add(i)
for i in npc_group:
    all_sprites.add(i)
for i in star_group:
    all_sprites.add(i)

# Game Loop ###############################################

# Game Update Variables
running = True
score = 0

while running:
    # Timing
    clock.tick(FPS)

    # Handle Events / Collect Inputs
    for event in pg.event.get():
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            running = False
        if event.type == pg.QUIT:
            running = False

    # Update
    all_sprites.update()

    if r.random() < 0.001:
        power = new_power()
        power_group.add(power)
        all_sprites.add(power)

    # If NPC hits player
    hits = pg.sprite.spritecollide(player, npc_group, True, pg.sprite.collide_circle)
    for hit in hits:
        npc.spawn()
        r.choice(expl_sounds).play()
        player.health -= hit.radius / 2

        if player.health <= 0:
            running = False

    hits = pg.sprite.groupcollide(npc_group, bullet_group, True, True)
    for hit in hits:
        score += 50 - hit.radius
        npc.spawn()
        r.choice(expl_sounds).play()

    # Check for player hitting powerup
    hits = pg.sprite.spritecollide(player, power_group, True, pg.sprite.collide_circle)
    for hit in hits:
        player.power = hit.type
        player.power_color = hit.color
        player.power_length = 1000

    # Draw / Render
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, "Score:{}".format(score), 20, RED, WIDTH / 2, 10)
    draw_bar(screen, 5, 15, GREEN, player.health)
    draw_bar(screen, 5, 30, player.power_color, player.power_length / 10)

    pg.display.flip()


# Quit
pg.quit()
