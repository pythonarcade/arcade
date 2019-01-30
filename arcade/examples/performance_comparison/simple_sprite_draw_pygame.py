"""
Pygame Sprite Stress Test

Simple program to test how fast we can draw sprites that aren't moving

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.performance_comparison.simple_sprite_draw_pygame
"""

import timeit
import pygame

# --- Constants ---

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Pygame Sprite Stress Test"


# This class represents the ball
# It derives from the "Sprite" class in Pygame
class Block(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("../images/coin_01.png").convert()

        # Set background color to be transparent. Adjust to WHITE if your
        # background is WHITE.
        self.image.set_colorkey(pygame.Color("black"))

        self.rect = self.image.get_rect()


def main():
    """ Main method """
    # Initialize Pygame
    pygame.init()

    # Set the height and width of the screen
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    pygame.display.set_caption(SCREEN_TITLE)

    # Sprite list
    all_sprites_list = pygame.sprite.Group()

    font = pygame.font.Font(None, 36)

    # Create the coins
    for x in range(0, SCREEN_WIDTH, 10):
        for y in range(0, SCREEN_HEIGHT, 10):
            # This represents a block
            block = Block()

            # Set a random location for the block
            block.rect.x = x
            block.rect.y = y

            # Add the block to the list of objects
            all_sprites_list.add(block)


    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    draw_time = 0

    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        # Clear the screen
        screen.fill(pygame.Color("white"))

        # Draw all the spites
        all_sprites_list.draw(screen)

        draw_time = timeit.default_timer() - draw_start_time

        sprite_count = len(all_sprites_list)
        output = f"Drawing time: {draw_time:.4f} for {sprite_count} sprites."
        text = font.render(output, True, pygame.Color("white"))
        screen.blit(text, [20, SCREEN_HEIGHT - 40])

        pygame.display.flip()

        # Limit to 60 frames per second
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
