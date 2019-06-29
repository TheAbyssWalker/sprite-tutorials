import pygame
import math
from enum import IntEnum, Enum

SIZE = WIDTH, HEIGHT = 1000, 700
BG_COLOR = pygame.Color ('grey')
FPS = 45
SPRITE_IMAGES = 10
WALK_SPEED = 4
ZOMBIE_SPEED = 1
RUN_SPEED = 8

def printRect (log_str, rect):
    rect_str = str (rect.top) + ", " + str (rect.bottom) + ", " + str (rect.left) + ", " + str (rect.right)
    print (log_str + " [top, bottom, left, right]: " + rect_str)

class Direction (IntEnum):
    UP      = 1
    DOWN    = 2
    LEFT    = 3
    RIGHT   = 4

class State (IntEnum):
    IDLE = 0
    WALK = 1
    RUN  = 2
    JUMP = 3  # Separate state
    DEAD = 4

class PlayerSprite (pygame.sprite.Sprite):
    def __init__ (self, pos, platform_group, spike_group, zombie_group, coin_group, screen_rect):
        super (PlayerSprite, self).__init__ ()
        self.dead_w             = int (75*986/579)
        self.dead_h             = int (100*796/763)
        self.alive_w            = 75
        self.alive_h            = 100
        # Load'em sprites
        self.images = {}
        self.images[State.IDLE] = []
        self.images[State.WALK] = []
        self.images[State.RUN]  = []
        self.images[State.JUMP] = []
        self.images[State.DEAD] = []
        for i in range (1, 11):
            img_path_i = "images/player/idle" + str (i) + ".png"
            img_path_w = "images/player/walk" + str (i) + ".png"
            img_path_j = "images/player/jump" + str (i) + ".png"
            img_path_d = "images/player/dead"  + str (i) + ".png"
            img_path_r = "images/player/run"  + str (i) + ".png"
            self.images[State.IDLE].append (pygame.transform.scale (pygame.image.load (img_path_i), (self.alive_w, self.alive_h)))
            self.images[State.WALK].append (pygame.transform.scale (pygame.image.load (img_path_w), (self.alive_w, self.alive_h)))
            self.images[State.RUN].append (pygame.transform.scale (pygame.image.load (img_path_r), (self.alive_w, self.alive_h)))
            self.images[State.JUMP].append (pygame.transform.scale (pygame.image.load (img_path_j), (self.alive_w, self.alive_h)))
            self.images[State.DEAD].append (pygame.transform.scale (pygame.image.load (img_path_d), (self.dead_w, self.dead_h)))

        self.screen_rect = screen_rect
        self.zombie_group = zombie_group
        self.platform_group = platform_group
        self.spike_group = spike_group
        self.coin_group = coin_group
        self.index = 0.0
        self.state = State.IDLE
        self.image = self.images[self.state][int (self.index)]

        self.is_dead            = False
        self.is_jumping         = False
        self.x_direction        = Direction.RIGHT
        self.y_direction        = Direction.DOWN
        self.score              = 0
        self.velocity           = 0     # Velocity for each tick
        self.acceleration       = 1     # Acceleration due to gravity
        self.gravity_acc        = 1
        self.total_jump_height  = 150
        self.unit_time          = 1
        self.up_time            = int (math.sqrt (self.total_jump_height * 2 / self.acceleration))
        self.x = self.init_x    = pos[0]
        self.y = self.init_y    = pos[1]
        self.w = self.init_w    = self.alive_w
        self.h = self.init_h    = self.alive_h
        #self.player_rect        = pygame.Rect (self.x + 20, self.y + 20, self.w - 20, self.h - 20)
        self.rect = pygame.Rect (self.x, self.y, self.w, self.h)

    def get_image (self):
        state = self.state
        if self.is_jumping:
            state = State.JUMP
        if self.x_direction == Direction.LEFT:
            return pygame.transform.flip (self.images[state][int (self.index
)], int (self.w / 2), 0)
        return self.images[state][int (self.index)]

    def update (self):
        # Function to update the index and image
        if self.is_dead:
            self.index = (self.index + 0.5)
            if self.index >= len (self.images[self.state]):
                self.index = len (self.images[self.state]) - 1
        elif self.is_jumping:
            self.calculate_next_jump ()
        else:
            self.index = (self.index + 0.5)
            self.gravity ()
            if self.index >= len (self.images[self.state]):
                self.index = 0

        self.get_collision ()
        rect = self.rect.clamp (self.screen_rect)
        if rect.bottom < self.rect.bottom:
            self.is_jumping = False
            self.velocity = 0
        self.rect = rect
        self.image  = self.get_image ()
        if not self.is_dead:
            self.state = State.IDLE
        #print (str (self.state) + " INSIDE else " + str (self.x_direction))

###############################################################################################
    def is_player_at_top_bottom (self, p_rect, c_rect):
        if (p_rect.top >= c_rect.top + 10 and p_rect.top < c_rect.bottom - 10) or \
                (p_rect.bottom <= c_rect.bottom - 10 and p_rect.bottom > c_rect.top + 10):
            return True
        return False

    def is_player_at_left_right (self, p_rect, c_rect):
        if (p_rect.left >= c_rect.left + 10 and p_rect.left < c_rect.right - 10) or \
                (p_rect.right <= c_rect.right - 10 and p_rect.right > c_rect.left + 10):
            return True
        return False

    def get_collision (self):
        min_y = self.rect.bottom
        #printRect ("Before collision player rect:", self.rect)
        for spike_sprite in pygame.sprite.spritecollide (self, self.spike_group, False, pygame.sprite.collide_rect_ratio(0.75)):
            self.rect.bottom = spike_sprite.rect.top
            self.dead ()

        for zombie_sprite in pygame.sprite.spritecollide (self, self.zombie_group, False, pygame.sprite.collide_rect_ratio(0.7)):
            self.dead ()

        for coin_sprite in pygame.sprite.spritecollide (self, self.coin_group, True):
            self.score += 1
            print ("Grabbed a coin, score : " + str (self.score))
        for collided_sprite in pygame.sprite.spritecollide (self, self.platform_group, False):
            # We need to check if player is in the top bottom range so that we can either clamp
            # the jump or consider the top as end of jump
            ret = self.is_player_at_left_right (self.rect, collided_sprite.rect)
            if ret:
                if self.rect.bottom > collided_sprite.rect.bottom and self.rect.top <= collided_sprite.rect.bottom:    # Bottom of platform
                    self.rect.top = collided_sprite.rect.bottom
                    #print ("Present at bottom")
                elif self.rect.top < collided_sprite.rect.top and self.rect.bottom >= collided_sprite.rect.top:  # Top of platform
                    #print ("Present at top")
                    self.rect.bottom = collided_sprite.rect.top
                    self.velocity = 0
                    self.is_jumping = False
            # Now that we updated top bottom coordinates, we need to check if the player is
            # on the right or left to stop moving through the collided sprites
            ret = self.is_player_at_top_bottom (self.rect, collided_sprite.rect)
            if ret:
                if self.rect.left < collided_sprite.rect.left and self.rect.right >= collided_sprite.rect.left:    # Left of platform
                    self.rect.right = collided_sprite.rect.left 
                    #print ("Present at left side")
                elif self.rect.right > collided_sprite.rect.right and self.rect.left <= collided_sprite.rect.right:  # Right of platform
                    self.rect.left = collided_sprite.rect.right
                    #print ("Present at right side")

            #printRect ("Collision rect", collided_sprite.rect)
        #printRect ("After collision player rect:", self.rect)
################################################################################################

    def walk (self, direction):
        self.x_direction = direction
        self.state = State.WALK
        speed = WALK_SPEED
        if direction == Direction.LEFT:
            speed = -WALK_SPEED
        self.move (speed, 0)

    def run (self, direction):
        self.x_direction = direction
        self.state = State.RUN
        speed = RUN_SPEED
        if direction == Direction.LEFT:
            speed = -RUN_SPEED
        self.move (speed, 0)

    def move (self, dx=0, dy=0):
        if not self.is_dead:
            #print (str (self.state) + " INSIDE Update " + str (self.x_direction))
            self.rect.x += dx
            self.rect.y += dy

    def is_alive (self):
        return not self.is_dead

    def clamp_rect (self):
        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH - 1
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT - 1
        if self.rect.top < 0:
            self.rect.top = 0

    def dead (self):
        self.state = State.DEAD
        self.is_jumping = False
        if not self.is_dead:
            self.index = 0
            self.is_dead = True
        self.rect.w = self.dead_w
        self.rect.h = self.dead_h

    def gravity (self):
        self.velocity += self.gravity_acc
        if self.velocity >= 30:
            self.velocity = 30
        self.move (0, int (self.velocity))

    def jump (self):
        if not self.is_dead:
            if not self.is_jumping:
                self.is_jumping = True
                self.index = 0
                self.velocity = int (self.acceleration * self.up_time)
                self.rect.y       -= int (self.velocity / 2)
                self.y_direction = Direction.UP

    def calculate_next_jump (self):
        if not self.is_dead:
            # Basically we need to increment the index wrt the formula:
            # step_size = num_of_jump_sprites / (2 * up_time)
            step_size = len (self.images[self.state]) / (2 * self.up_time)
            self.index = (self.index + step_size)
            if self.index >= len (self.images[self.state]):
                self.index = 0

            self.velocity -= int (self.acceleration * self.unit_time)
            self.rect.y -= self.velocity
            #if self.rect.bottom >= HEIGHT:
            #    self.rect.bottom = HEIGHT - 1
            #    self.is_jumping = False
            #    self.velocity = 0
                #self.dead ()
            #print (str (self.rect.y) + " "  + str (min_y))

class ZombieSprite (pygame.sprite.Sprite):
    def __init__ (self, bound_rect):
        super (ZombieSprite, self).__init__ ()

        self.w = 75
        self.h = 100
        self.images = []
        for i in range (1, 11):
            img_path = "images/zombie/walk" + str (i) + ".png"
            self.images.append (pygame.transform.scale (pygame.image.load (img_path), (self.w, self.h)))

        self.direction = Direction.RIGHT
        self.bound_rect = bound_rect
        self.index = 0.0
        self.image = self.images[int (self.index)]
        self.rect = self.image.get_rect ()
        self.rect.left      = bound_rect.left
        self.rect.bottom    = bound_rect.bottom

    def update (self):
        self.index += 0.25
        if self.index >= len (self.images):
            self.index = 0

        if self.rect.right >= self.bound_rect.right:
            self.direction = Direction.LEFT
        if self.rect.left <= self.bound_rect.left:
            self.direction = Direction.RIGHT

        if self.direction == Direction.RIGHT:
            self.rect.x += ZOMBIE_SPEED
            self.image = self.images[int (self.index)]
        else:
            self.rect.x -= ZOMBIE_SPEED
            self.image = pygame.transform.flip (self.images[int (self.index)], int (self.rect.w / 2), 0)


class PlatformSprite (pygame.sprite.Sprite):
    def __init__ (self, rect, color):
        super (PlatformSprite, self).__init__ ()
        self.image = pygame.Surface([rect.w, rect.h])
        self.image.fill (pygame.Color (color))
        self.rect = self.image.get_rect ()
        self.rect.x = rect.x
        self.rect.y = rect.y

class SpikeSprite (pygame.sprite.Sprite):
    def __init__ (self, rect, color):
        super (SpikeSprite, self).__init__ ()
        self.image = pygame.Surface([rect.w, rect.h])
        self.image.fill (pygame.Color (color))
        self.rect = self.image.get_rect ()
        self.rect.x = rect.x
        self.rect.y = rect.y

class CoinSprite (pygame.sprite.Sprite):
    def __init__ (self, rect):
        super (CoinSprite, self).__init__ ()
        self.image = pygame.Surface([rect.w, rect.h])
        self.image.fill (pygame.Color ("gold"))
        self.rect = self.image.get_rect ()
        self.rect.x = rect.x
        self.rect.y = rect.y

class GameLoop ():
    def __init__ (self):
        pygame.init ()

        self.screen = pygame.display.set_mode (SIZE)
        self.screen_rect = self.screen.get_rect ()
        self.clock = pygame.time.Clock ()

    def init_level (self, level=None):
        if level is None:
            ground1 = PlatformSprite (pygame.Rect (900, 500, 100, 30), "black")
            ground2 = PlatformSprite (pygame.Rect (500, 400, 100, 80), "black")
            ground3 = PlatformSprite (pygame.Rect (0, 500, 300, 30), "black")
            coin    = CoinSprite (pygame.Rect (920, 450, 30, 40))
            spike  = SpikeSprite (pygame.Rect (0, 650, WIDTH, 50), "red")
            zombie = ZombieSprite (pygame.Rect (0, 470, 300, 30))
            self.coins = pygame.sprite.Group (coin)
            self.spikes  = pygame.sprite.Group (spike)
            self.platforms = pygame.sprite.Group (ground1, ground2, ground3)
            self.zombies = pygame.sprite.Group (zombie)
            self.player = PlayerSprite ((100, 200), self.platforms, self.spikes, self.zombies, self.coins, self.screen_rect)
            self.actors = pygame.sprite.Group (self.player, zombie, coin)

    def get_events (self):
        for event in pygame.event.get ():
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_q) or \
                event.type == pygame.QUIT:
                print ("QUIT")
                pygame.quit ()
                quit ()
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_d):
                self.player.dead ()
                break
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                self.player.jump ()
                #print ("Jumping here " + str (int (Direction.UP)))

        if self.player.is_alive ():
            keys = pygame.key.get_pressed ()
            if keys[pygame.K_LEFT]:
                if pygame.key.get_mods () & pygame.KMOD_SHIFT:
                    self.player.walk (Direction.LEFT)
                else:
                    self.player.run (Direction.LEFT)
            elif keys[pygame.K_RIGHT]:
                if pygame.key.get_mods () & pygame.KMOD_SHIFT:
                    self.player.walk (Direction.RIGHT)
                else:
                    self.player.run (Direction.RIGHT)

    def update_frame (self):
        self.screen.fill (BG_COLOR)

        self.actors.update ()

        self.actors.draw (self.screen)
        self.platforms.draw (self.screen)
        self.spikes.draw (self.screen)

        pygame.display.update ()

        self.clock.tick (FPS)


if __name__ == '__main__':
    print ("Start")
    game = GameLoop ()
    game.init_level ()
    while True:
        game.get_events ()
        game.update_frame ()
