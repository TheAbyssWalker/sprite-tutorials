import pygame
import math
from enum import IntEnum, Enum

SIZE = WIDTH, HEIGHT = 1000, 700
BG_COLOR = pygame.Color ('grey')
FPS = 45
SPRITE_IMAGES = 10
WALK_SPEED = 3
RUN_SPEED = 10

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
    def __init__ (self, platform_group, spike_group, screen_rect):
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
            img_path_i = "images/idle" + str (i) + ".png"
            img_path_w = "images/walk" + str (i) + ".png"
            img_path_j = "images/jump" + str (i) + ".png"
            img_path_d = "images/dead"  + str (i) + ".png"
            img_path_r = "images/run"  + str (i) + ".png"
            self.images[State.IDLE].append (pygame.transform.scale (pygame.image.load (img_path_i), (self.alive_w, self.alive_h)))
            self.images[State.WALK].append (pygame.transform.scale (pygame.image.load (img_path_w), (self.alive_w, self.alive_h)))
            self.images[State.RUN].append (pygame.transform.scale (pygame.image.load (img_path_r), (self.alive_w, self.alive_h)))
            self.images[State.JUMP].append (pygame.transform.scale (pygame.image.load (img_path_j), (self.alive_w, self.alive_h)))
            self.images[State.DEAD].append (pygame.transform.scale (pygame.image.load (img_path_d), (self.dead_w, self.dead_h)))

        self.screen_rect = screen_rect
        self.platform_group = platform_group
        self.spike_group = spike_group
        self.index = 0.0
        self.state = State.IDLE
        self.image = self.images[self.state][int (self.index)]

        self.is_dead            = False
        self.is_jumping         = False
        self.x_direction        = Direction.RIGHT
        self.y_direction        = Direction.DOWN
        self.velocity           = 0     # Velocity for each tick
        self.acceleration       = 1     # Acceleration due to gravity
        self.gravity_acc        = 1
        self.total_jump_height  = 300
        self.unit_time          = 1
        self.up_time            = int (math.sqrt (self.total_jump_height * 2 / self.acceleration))
        self.x = self.init_x    = 100
        self.y = self.init_y    = 350
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
        for spike_sprite in pygame.sprite.spritecollide (self, self.spike_group, False):
            self.rect.bottom = spike_sprite.rect.top
            self.dead ()

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

    def move (self, dx=0, dy=0):
        if not self.is_dead:
            #print (str (self.state) + " INSIDE Update " + str (self.x_direction))
            self.rect.x += dx
            self.rect.y += dy

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

def main ():
    pygame.init ()

    screen = pygame.display.set_mode (SIZE)
    screen_rect = screen.get_rect ()

    ground1 = PlatformSprite (pygame.Rect (0, 200, 100, 30), "black")
    ground2 = PlatformSprite (pygame.Rect (500, 400, 100, 30), "black")
    ground3 = PlatformSprite (pygame.Rect (0, 500, 300, 30), "black")
    spike  = SpikeSprite (pygame.Rect (0, 650, WIDTH, 50), "red")
    platforms = pygame.sprite.Group (ground1, ground2, ground3)
    spikes  = pygame.sprite.Group (spike)
    player = PlayerSprite (platforms, spikes, screen_rect)
    actors = pygame.sprite.Group (player)

    clock = pygame.time.Clock ()

    while True:
        for event in pygame.event.get ():
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_q) or \
                event.type == pygame.QUIT:
                print ("QUIT")
                pygame.quit ()
                quit ()
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_d):
                player.dead ()
                break
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                player.jump ()
                #print ("Jumping here " + str (int (Direction.UP)))

        speed = 0
        if player.state != State.DEAD:
            keys = pygame.key.get_pressed ()
            if keys[pygame.K_LEFT]:
                player.x_direction = Direction.LEFT
                player.state = State.WALK
                speed = -WALK_SPEED
                if pygame.key.get_mods () & pygame.KMOD_SHIFT:
                    speed = -RUN_SPEED
                    player.state = State.RUN
                #player.move (speed, 0)
            elif keys[pygame.K_RIGHT]:
                player.x_direction = Direction.RIGHT
                player.state = State.WALK
                speed = WALK_SPEED
                if pygame.key.get_mods () & pygame.KMOD_SHIFT:
                    speed = RUN_SPEED
                    player.state = State.RUN
                #player.move (speed, 0)

        player.move (speed, 0)

        screen.fill (BG_COLOR)

        actors.update ()

        actors.draw (screen)
        platforms.draw (screen)
        spikes.draw (screen)

        pygame.display.update ()

        clock.tick (FPS)


if __name__ == '__main__':
    print ("Start")
    main ()
