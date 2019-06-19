import pygame
from enum import Enum

SIZE = WIDTH, HEIGHT = 600, 400     # Resolution of the screen
BG_COLOR = pygame.Color ('white')   # BG color
FPS = 40                            # Need I say anything more?

class Direction (Enum):
    LEFT    = 1
    RIGHT   = 2
    UP      = 3
    DOWN    = 4

class TheSprite (pygame.sprite.Sprite):
    def __init__ (self):
        super (TheSprite, self).__init__ ()
        # Load all those beautiful sprites
        self.images = []
        self.images.append (pygame.image.load ('images/walk1.png'))
        self.images.append (pygame.image.load ('images/walk2.png'))
        self.images.append (pygame.image.load ('images/walk3.png'))
        self.images.append (pygame.image.load ('images/walk4.png'))
        self.images.append (pygame.image.load ('images/walk5.png'))
        self.images.append (pygame.image.load ('images/walk6.png'))
        self.images.append (pygame.image.load ('images/walk7.png'))
        self.images.append (pygame.image.load ('images/walk8.png'))
        self.images.append (pygame.image.load ('images/walk9.png'))
        self.images.append (pygame.image.load ('images/walk10.png'))

        # Index to hold which image to load next from the array
        self.index = 0

        # Now the image that we will load
        self.image = self.images[self.index]

        self.x = 5
        self.y = 100
        self.w = 150
        self.h = 198
        self.direction = Direction.RIGHT
        # Creating a rect at position (5, 5) of size (150, 198) which is the size of sprite
        self.rect = pygame.Rect (self.x, self.y, self.w, self.h)

    def update (self):
        # When the update method is called we will increment the index
        self.index = (self.index + 1) % 10

        if self.x + self.w - 25 >= WIDTH:
            self.direction = Direction.LEFT
        if self.x + 25<= 0:
            self.direction = Direction.RIGHT
        # Update image to load
        if self.direction == Direction.LEFT:
            self.image = pygame.transform.flip (self.images[self.index], int (self.w/2), 0)
            self.x -= 5
        else:
            self.image = self.images[self.index]
            self.x += 5

        # Update position
        self.rect = pygame.Rect (self.x, self.y, self.w, self.h)


def main():
    pygame.init ()

    screen = pygame.display.set_mode (SIZE)

    the_sprite = TheSprite ()

    the_group = pygame.sprite.Group (the_sprite)

    clock = pygame.time.Clock ()

    print ("Done init")
    while True:
        for event in pygame.event.get():
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_q) or \
                event.type == pygame.QUIT:
                print ("QUIT")
                pygame.quit ()
                quit ()

        screen.fill (BG_COLOR)

        the_group.update ()

        the_group.draw (screen)

        pygame.display.update ()

        clock.tick (FPS)


if __name__ == '__main__':
    print ("Start")
    main ()
