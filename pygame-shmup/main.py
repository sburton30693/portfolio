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
        self.speed = r.choice((10, 11))

    def update(self):
        self.rect.y += self.speed

        if self.rect.top >= HEIGHT:
            self.rect.centerx = r.randint(0, WIDTH)
            self.rect.bottom = 0


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, speedx=0, size=5):
        super(Bullet, self).__init__()
        # self.image = pg.Surface((size, 20))
        # self.image.fill(BLUE)
        self.image = pg.transform.scale(bullet_img, (int(size), 20))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedx = speedx
        self.speedy = -20

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx

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
        self.base_speed_num = 7
        self.speed_num = self.base_speed_num
        self.base_size = 5
        self.bullet_size = self.base_size
        self.left_image = False
        self.right_image = False
        self.last_shot = pg.time.get_ticks()
        self.base_delay = 350
        self.shot_delay = self.base_delay
        self.power = ""
        self.power_timer = pg.time.get_ticks()
        self.power_level = 1
        self.lives = 3
        self.hide_timer = pg.time.get_ticks()
        self.hidden = False

    def update(self):
        key_states = pg.key.get_pressed()
        self.speedx = 0

        if pg.time.get_ticks() - self.power_timer > POWERUP_TIME:
            self.bullet_size = self.base_size
            self.shot_delay = self.base_delay
            self.speed_num = self.base_speed_num

        # Un-hide if hidden
        if self.hidden and (pg.time.get_ticks() - self.hide_timer > 3000):
            self.hidden = False
            self.health = 100
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = (HEIGHT - (HEIGHT * 0.1))

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



        if key_states[pg.K_DOWN]:
            self.power = "Rapid Fire"
            self.power_length = 1000
        if key_states[pg.K_i]:
            self.power_level += 1

        # Fire a bullet if holding space
        if key_states[pg.K_SPACE] and not self.hidden:
            self.shoot()

        self.rect.x += self.speedx

        # Keep from leaving the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def hide(self):
        # hide the player temporarily
        self.lives -= 1
        self.hidden = True
        self.hide_timer = pg.time.get_ticks()
        self.rect.center = (WIDTH / 2, -200)
        self.power_length = 0
        self.power = ""

    def shoot_single(self):
        bullet = Bullet(self.rect.centerx, self.rect.top - 1, size=self.bullet_size)
        bullet_group.add(bullet)
        all_sprites.add(bullet)
        pew_sound.play(maxtime=100)

    def shoot_dual(self, spread=False):
        if spread:
            bulletl = Bullet(self.rect.left, self.rect.top - 1, -1, self.bullet_size)
            bulletr = Bullet(self.rect.right, self.rect.top - 1, 1, self.bullet_size)
        else:
            bulletl = Bullet(self.rect.left, self.rect.top - 1, size=self.bullet_size)
            bulletr = Bullet(self.rect.right, self.rect.top - 1, size=self.bullet_size)
        bullet_group.add(bulletl)
        bullet_group.add(bulletr)
        all_sprites.add(bulletl)
        all_sprites.add(bulletr)
        pew_sound.play(maxtime=100)

    def shoot(self):
        now = pg.time.get_ticks()

        if now - self.last_shot >= self.shot_delay:
            self.last_shot = now

            if self.power_level == 1:
                self.shoot_single()
            elif self.power_level == 2:
                self.shoot_dual()
            elif self.power_level == 3:
                self.shoot_dual()
                self.shoot_single()
            elif self.power_level >= 4:
                self.shoot_dual(True)
                self.shoot_single()

    def reset_powers(self):
        self.bullet_size = self.base_size
        self.shot_delay = self.base_delay
        self.speed_num = self.base_speed_num

    def power_percent_left(self):
        return 100 - 100 * (pg.time.get_ticks() - self.power_timer) / POWERUP_TIME

    def heal(self, num):
        self.health += num

        if self.health > 100:
            self.health = 100

    def gun_power_up(self):
        self.power_level += 1

    def gun_power_down(self):
        self.power_level -= 1

        if self.power_level < 1:
            self.power_level = 1

    def fuel_power_up(self):
        self.reset_powers()

        self.speed_num = 12
        self.power_timer = pg.time.get_ticks()

    def big_bullet_power_up(self):
        self.reset_powers()

        self.bullet_size = 50
        self.power_timer = pg.time.get_ticks()

    def ammun_power_up(self):
        self.reset_powers()

        self.shot_delay = 50
        self.power_timer = pg.time.get_ticks()


class NPC(pg.sprite.Sprite):
    def __init__(self, difficulty=0):
        super(NPC, self).__init__()
        # self.image = pg.Surface((25, 25))
        # self.image.fill(RED)
        self.image = enemy_img
        self.size = r.randint(25, int(60 + difficulty))
        self.image_orig = pg.transform.scale(enemy_img, (self.size, self.size))
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.new_image = self.image
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width/2 * 0.75)
        #pg.draw.circle(self.image_orig, RED, self.rect.center, self.radius)
        self.rect.centerx = r.randint(0, WIDTH)
        self.rect.bottom = 0
        self.speed = [r.random() * 10 - 5, r.random() * 15 + 5 + difficulty/20]
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
            self.kill()
            spawn_npc(difficulty)

        if self.rect.bottom < 0:
            self.kill()
            spawn_npc(difficulty)


class Explosion(pg.sprite.Sprite):
    def __init__(self, center, size):
        super(Explosion, self).__init__()
        self.size = size
        self.image = explosion_anim[size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.frame_rate = 50
        self.last_update = pg.time.get_ticks()

    def update(self):
        now = pg.time.get_ticks()

        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1

            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class PowerUp(pg.sprite.Sprite):
    def __init__(self, center):
        super(PowerUp, self).__init__()
        self.type = r.choice(powerups_chance)
        self.image = power_imgs[self.type]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed = 3

    def update(self):
        self.rect.y += self.speed

        if self.rect.top >= HEIGHT:
            self.kill()


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

powerups_list = ["shield", "gun", "fuel", "big", "ammunition"]
powerups_chance = ["ammunition", "ammunition", "gun", "gun", "big", "big", "fuel", "fuel", "fuel", "shield", "shield", "shield", "shield"]

POWERUP_TIME = 10000

# Folders #################################################
game_folder = path.dirname(__file__)
imgs_folder = path.join(game_folder, "imgs")
scores_folder = path.join(game_folder, "scores")
snds_folder = path.join(game_folder, "snds")
animation_folder = path.join(imgs_folder, "animations")
enemy_animation_folder = path.join(animation_folder, "enemy")
player_animation_folder = path.join(animation_folder, "player")
player_img_folder = path.join(imgs_folder, "player")
enemy_img_folder = path.join(imgs_folder, "enemy")
power_img_folder = path.join(imgs_folder, "pows")
background_img_folder = path.join(imgs_folder, "backgrounds")


# Game Functions ##########################################
def draw_text(surface, text, size, x, y, color=WHITE):
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)


def draw_bar(surface, x, y, pct, color):
    if pct < 0:
        pct = 0

    bar_len = 200
    bar_height = 15
    fill = (pct / 100) * bar_len
    outline_rect = pg.Rect(x, y, bar_len, bar_height)
    fill_rect = pg.Rect(x, y, fill, bar_height)

    pg.draw.rect(surface, color, fill_rect)
    pg.draw.rect(surface, WHITE, outline_rect, 3)


def draw_lives(surface, x, y, lives, img):
    img_rect = img.get_rect()
    img_rect.y = y

    for i in range(lives):
        img_rect.x = x + 30 * i
        surface.blit(img, img_rect)


def show_game_over_screen(screen):
    screen.blit(background, background_rect)
    draw_text(screen, "SHMUP!", 64, WIDTH / 2, HEIGHT / 4, WHITE)
    draw_text(screen, "Arrow/WASD keys to move and Space to fire.", 22, WIDTH / 2, HEIGHT / 2, YELLOW)
    draw_text(screen, "Press a key to begin or Q to quit", 18, WIDTH / 2, HEIGHT * 3 / 4, YELLOW)
    pg.display.flip()

    waiting = True
    while waiting:
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                exit()

            if event.type == pg.KEYUP:
                if event.key == pg.K_q:
                    exit()
                else:
                    waiting = False


def reset():
    global player, player_expl, score, difficulty

    # Remove every sprite from every group

    # Create Game Objects
    player = Player()
    player_expl = None

    for i in range(15):
        npc = NPC()
        npc_group.add(npc)

    for i in range(50):
        star = Star()
        star_group.add(star)

    # Add Objects to Sprite Groups
    player_group.add(player)

    for i in player_group:
        all_sprites.add(i)
    for i in npc_group:
        all_sprites.add(i)
    for i in star_group:
        all_sprites.add(i)

    # Reset score and difficulty
    score = 0
    difficulty = 0


def spawn_npc(diff=0):
    new_npc = NPC(diff)
    npc_group.add(new_npc)
    all_sprites.add(new_npc)


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
player_life_img = pg.transform.scale(player_img, (25, 19))
player_life_img.set_colorkey(BLACK)

enemy_img = pg.image.load(path.join(enemy_img_folder, "meteor.png")).convert()

bullet_img = pg.image.load(path.join(player_img_folder, "laser.png")).convert()

explosion_anim = {}
explosion_anim["large"] = []
explosion_anim["small"] = []
explosion_anim["player"] = []

for i in range(9):
    fn = "regularExplosion0{}.png".format(i)
    img = pg.image.load(path.join(enemy_animation_folder, fn)).convert()
    img.set_colorkey(BLACK)
    img_large = pg.transform.scale(img, (100, 100))
    img_small = pg.transform.scale(img, (40, 40))
    explosion_anim["large"].append(img_large)
    explosion_anim["small"].append(img_small)

    fn = "sonicExplosion0{}.png".format(i)
    img = pg.image.load(path.join(player_animation_folder, fn)).convert()
    img.set_colorkey(BLACK)
    explosion_anim["player"].append(img)

power_imgs = {}
for i in range(len(powerups_list)):
    fn = "img_{}.png".format(i)
    power_imgs[powerups_list[i]] = pg.image.load(path.join(power_img_folder, fn)).convert()
    power_imgs[powerups_list[i]].set_colorkey(BLACK)

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

# Game Loop ###############################################

# Game Update Variables
running = True
game_over = True
score = 0
difficulty = 0

while running:
    if game_over:
        show_game_over_screen(screen)
        game_over = False

        # Clear Groups
        all_sprites = pg.sprite.Group()
        player_group = pg.sprite.Group()
        npc_group = pg.sprite.Group()
        star_group = pg.sprite.Group()
        power_group = pg.sprite.Group()
        bullet_group = pg.sprite.Group()

        reset()

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

    # If NPC hits player
    hits = pg.sprite.spritecollide(player, npc_group, True, pg.sprite.collide_circle)
    for hit in hits:
        spawn_npc(difficulty)
        all_sprites.add(Explosion(hit.rect.center, "small"))
        r.choice(expl_sounds).play()
        player.health -= hit.radius / 2
        player.gun_power_down()

        if player.health <= 0:
            player_expl = Explosion(player.rect.center, "player")
            all_sprites.add(player_expl)
            player.hide()

            if player.lives <= 0:
                player.kill()

    # If player is out of lives and the explosion animation ends, end the game
    if not player.alive() and not player_expl.alive():
        #running = False
        game_over = True

    hits = pg.sprite.groupcollide(npc_group, bullet_group, True, True)
    for hit in hits:
        score += 50 - hit.radius
        difficulty = score / 3000
        all_sprites.add(Explosion(hit.rect.center, "large"))
        spawn_npc(difficulty)
        r.choice(expl_sounds).play()

        # Change of an asteroid dropping a power-up
        if r.random() < 5/100:
            power = PowerUp(hit.rect.center)
            power_group.add(power)
            all_sprites.add(power)

    # Check for player hitting powerup
    hits = pg.sprite.spritecollide(player, power_group, True, pg.sprite.collide_circle)
    for hit in hits:
        if hit.type == "shield":
            player.heal(r.randint(15, 20))
        elif hit.type == "gun":
            player.gun_power_up()
        elif hit.type == "fuel":
            player.fuel_power_up()
        elif hit.type == "big":
            player.big_bullet_power_up()
        elif hit.type == "ammunition":
            player.ammun_power_up()

    # Draw / Render
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)

    draw_text(screen, "Score:{}".format(score), 20, WIDTH / 2, 10, RED)
    draw_bar(screen, 5, 15, player.health, GREEN)
    draw_bar(screen, 5, 30, player.power_percent_left(), BLUE)
    draw_lives(screen, WIDTH - 100, 10, player.lives, player_life_img)

    pg.display.flip()


# Quit
pg.quit()
