import pygame
import math
from enum import IntEnum, Enum

SIZE = WIDTH, HEIGHT = 1000, 700
BG_COLOR = pygame.Color ('white')
FPS = 45
SPRITE_IMAGES = 10

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

class PlayerSprite (pygame.sprite.Sprite):
    def __init__ (self):
        super (PlayerSprite, self).__init__ ()
        # Load'em sprites
        self.images = {}
        self.images[State.IDLE] = []
        self.images[State.WALK] = []
        self.images[State.RUN]  = []
        self.images[State.JUMP] = []
        for i in range (1, 11):
            img_path_i = "images/idle" + str (i) + ".png"
            img_path_w = "images/walk" + str (i) + ".png"
            img_path_j = "images/jump" + str (i) + ".png"
            img_path_r = "images/run"  + str (i) + ".png"
            self.images[State.IDLE].append (pygame.transform.scale (pygame.image.load (img_path_i), (150, 200)))
            self.images[State.WALK].append (pygame.transform.scale (pygame.image.load (img_path_w), (150, 200)))
            self.images[State.RUN].append (pygame.transform.scale (pygame.image.load (img_path_r), (150, 200)))
            self.images[State.JUMP].append (pygame.transform.scale (pygame.image.load (img_path_j), (150, 200)))

        self.index = 0.0
        self.state = State.IDLE
        self.image = self.images[self.state][int (self.index)]

        self.is_jumping         = False
        self.x_direction        = Direction.RIGHT
        self.y_direction        = Direction.DOWN
        self.velocity           = 0     # Velocity for each tick
        self.acceleration       = 1     # Acceleration due to gravity
        self.total_jump_height  = 100
        self.unit_time          = 1
        self.up_time            = int (math.sqrt (self.total_jump_height * 2 / self.acceleration))
        self.x = self.init_x    = 100
        self.y = self.init_y    = 350
        self.w = self.init_w    = 150
        self.h = self.init_h    = 200
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
        if self.is_jumping:
            self.jump ()
        else:
            self.index = (self.index + 0.5)
            if self.index >= len (self.images[self.state]):
                self.index = 0

        self.image  = self.get_image ()
        self.rect   = pygame.Rect (self.x, self.y, self.w, self.h)
        #print (str (self.state) + " INSIDE else " + str (self.x_direction))

    def move (self, speed=5):
        if self.state == State.WALK or self.state == State.RUN:
            #print (str (self.state) + " INSIDE Update " + str (self.x_direction))
            if self.x_direction is Direction.LEFT:
                self.x -= speed
            else:
                self.x += speed
            #self.x += (self.x_direction * 5)
            if self.x + self.w >= WIDTH:
                self.x = WIDTH - self.w
            if self.x <= 0:
                self.x = 0
            #print (str (self.x) + " "  + str (self.velocity))


    def jump (self):
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity = int (self.acceleration * self.up_time)
            self.y       -= int (self.velocity / 2)
            self.y_direction = Direction.UP
        else:
            # Basically we need to increment the index wrt the formula:
            # step_size = num_of_jump_sprites / (2 * up_time)
            step_size = len (self.images[self.state]) / (2 * self.up_time)
            self.index = (self.index + step_size)
            if self.index >= len (self.images[self.state]):
                self.index = 0

            self.velocity -= int (self.acceleration * self.unit_time)
            self.y -= self.velocity
            if self.y >= self.init_y:
                self.y      = self.init_y
                self.is_jumping = False
                self.index = 0
                self.y_direction = Direction.DOWN
            #print (str (self.y) + " "  + str (self.velocity))

def main ():
    pygame.init ()

    screen = pygame.display.set_mode (SIZE)

    the_sprite = PlayerSprite ()
    the_group = pygame.sprite.Group (the_sprite)

    clock = pygame.time.Clock ()

    while True:
        for event in pygame.event.get ():
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_q) or \
                event.type == pygame.QUIT:
                print ("QUIT")
                pygame.quit ()
                quit ()
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                the_sprite.jump ()
                print ("Jumping here " + str (int (Direction.UP)))

        keys = pygame.key.get_pressed ()
        if keys[pygame.K_LEFT]:
            the_sprite.state = State.WALK
            the_sprite.x_direction = Direction.LEFT
            speed = 5
            if pygame.key.get_mods () & pygame.KMOD_SHIFT:
                the_sprite.state = State.RUN
                speed = 12
            the_sprite.move (speed)
        elif keys[pygame.K_RIGHT]:
            the_sprite.state = State.WALK
            the_sprite.x_direction = Direction.RIGHT
            speed = 5
            if pygame.key.get_mods () & pygame.KMOD_SHIFT:
                the_sprite.state = State.RUN
                speed = 12
            the_sprite.move (speed)
        else:
            the_sprite.state = State.IDLE

        screen.fill (BG_COLOR)

        the_group.update ()

        the_group.draw (screen)

        pygame.display.update ()

        clock.tick (FPS)


if __name__ == '__main__':
    print ("Start")
    main ()
