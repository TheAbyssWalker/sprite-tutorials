import pygame
import math
from enum import Enum

SIZE = WIDTH, HEIGTH = 600, 400
BG_COLOR = pygame.Color ('white')
FPS = 40

class Direction (Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class TheSprite (pygame.sprite.Sprite):
    def __init__ (self):
        super (TheSprite, self).__init__ ()
        # Load'em sprites
        self.images = []
        for i in range (1, 11):
            img_path = "images/jump" + str (i) + ".png"
            self.images.append (pygame.transform.scale (pygame.image.load (img_path), (150, 198)))

        img_path = "images/idle10.png"
        self.images.append (pygame.transform.scale (pygame.image.load (img_path), (150, 198)))

        # Index to load corresponding image
        self.index = 10.0     # Last image is the idle image

        self.image = self.images[int (self.index)]

        self.velocity           = 0     # Velocity for each tick while jumping
        self.acceleration       = 1     # Basically acceleration due to gravity (g)
        self.total_jump_height  = 50    # Number of pixels he can jump
        self.y_distance         = 0
        self.time_tick          = 1     # Unit time (tick of the pygame clock)
        self.is_jumping         = False
        self.x = self.init_x = 100
        self.y = self.init_y = 100
        self.w = self.init_w = 150
        self.h = self.init_h = 198
        self.rect = pygame.Rect (self.x, self.y, self.w, self.h)

    def update (self):
        # When method is called we will update the index
        if self.is_jumping:
            # Basically we need to increment the index wrt the formula:
            # step_size = num_of_jump_sprites / (2 * up_time)
            self.index = (self.index + 0.5)
            if self.index >= 10.0:
                self.index = 0

            # Subtract acceleration per unit time in each tick from velocity
            self.velocity -= int (self.acceleration * self.time_tick)
            # Subtract the velocity from y. We need to subtract because
            # the Y axis is reversed in images
            self.y -= self.velocity
            # If it reaches its initial y pos, it means jump is done, so stop
            if self.y >= self.init_y:
                self.y = self.init_y
                self.is_jumping = False
            #print (str (self.y) + " "  + str (self.velocity))
        else:
            # get idle image
            self.index = 10

        self.image = self.images[int (self.index)]
        self.rect = pygame.Rect (self.x, self.y, self.w, self.h)

    def jump (self):
        # This check is required so that the jump does not start midway
        # when we press the jump button while jumping
        if not self.is_jumping:
            self.is_jumping = True
            self.up_time    = int (math.sqrt (self.total_jump_height * 2 / self.acceleration))
            self.velocity   = int (self.acceleration * self.up_time)
            self.y         -= int (self.velocity / 2)

def main ():
    pygame.init ()

    screen = pygame.display.set_mode (SIZE)

    the_sprite = TheSprite ()
    the_group = pygame.sprite.Group (the_sprite)

    clock = pygame.time.Clock ()

    while True:
        for event in pygame.event.get ():
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_q) or \
                event.type == pygame.QUIT:
                print ("QUIT")
                pygame.quit ()
                quit ()
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_j):
                the_sprite.jump ()
                print ("Jumping")

        screen.fill (BG_COLOR)

        the_group.update ()

        the_group.draw (screen)

        pygame.display.update ()

        clock.tick (FPS)


if __name__ == '__main__':
    print ("Start")
    main ()
