"""
Sample Python/Pygame Programs
Simpson College Computer Science
http://programarcadegames.com/
"""

# noinspection PyPackageRequirements
import pygame
import random
import os
import time
import timeit
import collections

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# --- Constants ---
SPRITE_SCALING_COIN = 0.09
SPRITE_SCALING_PLAYER = 0.5
SPRITE_NATIVE_SIZE = 128
SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * SPRITE_SCALING_COIN)
COIN_COUNT_INCREMENT = 500

STOP_COUNT = 12000
RESULTS_FILE = "stress_test_collision_pygame_1_9_6.csv"

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Moving Sprite Stress Test"


class FPSCounter:
    def __init__(self):
        self.time = time.perf_counter()
        self.frame_times = collections.deque(maxlen=60)

    def tick(self):
        t1 = time.perf_counter()
        dt = t1 - self.time
        self.time = t1
        self.frame_times.append(dt)

    def get_fps(self):
        total_time = sum(self.frame_times)
        if total_time == 0:
            return 0
        else:
            return len(self.frame_times) / sum(self.frame_times)


class Coin(pygame.sprite.Sprite):
    """
    This class represents the ball
    It derives from the "Sprite" class in Pygame
    """

    def __init__(self):
        """ Constructor. Pass in the color of the block,
        and its x and y position. """
        # Call the parent class (Sprite) constructor
        super().__init__()

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        image = pygame.image.load("../../resources/images/items/coinGold.png")
        rect = image.get_rect()
        image = pygame.transform.scale(image,
                                       (int(rect.width * SPRITE_SCALING_COIN), int(rect.height * SPRITE_SCALING_COIN)))
        self.image = image.convert()
        self.image.set_colorkey(BLACK)

        # Fetch the rectangle object that has the dimensions of the image
        # image.
        # Update the position of this object by setting the values
        # of rect.x and rect.y
        self.rect = self.image.get_rect()


class Player(pygame.sprite.Sprite):
    """
    This class represents the ball
    It derives from the "Sprite" class in Pygame
    """

    def __init__(self):
        """ Constructor. Pass in the color of the block,
        and its x and y position. """
        # Call the parent class (Sprite) constructor
        super().__init__()

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        image = pygame.image.load("../../resources/images/animated_characters/female_person/femalePerson_idle.png")
        rect = image.get_rect()
        image = pygame.transform.scale(image, (
            int(rect.width * SPRITE_SCALING_PLAYER), int(rect.height * SPRITE_SCALING_PLAYER)))
        self.image = image.convert()
        self.image.set_colorkey(BLACK)

        # Fetch the rectangle object that has the dimensions of the image
        # image.
        # Update the position of this object by setting the values
        # of rect.x and rect.y
        self.rect = self.image.get_rect()

        self.change_x = 0
        self.change_y = 0

    def update(self):
        """ Called each frame. """
        self.rect.x += self.change_x
        self.rect.y += self.change_y


class MyGame:
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Variables that will hold sprite lists
        self.coin_list = None

        self.processing_time = 0
        self.draw_time = 0
        self.program_start_time = timeit.default_timer()
        self.sprite_count_list = []
        self.fps_list = []
        self.processing_time_list = []
        self.drawing_time_list = []
        self.last_fps_reading = 0
        self.fps = FPSCounter()

        # Initialize Pygame
        pygame.init()

        # Set the height and width of the screen
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

        # This is a list of every sprite. All blocks and the player block as well.
        self.coin_list = pygame.sprite.Group()
        self.player_list = pygame.sprite.Group()

        # Create the player instance
        self.player = Player()

        self.player.rect.x = random.randrange(SPRITE_SIZE, SCREEN_WIDTH - SPRITE_SIZE)
        self.player.rect.y = random.randrange(SPRITE_SIZE, SCREEN_HEIGHT - SPRITE_SIZE)
        self.player.change_x = 3
        self.player.change_y = 5

        self.player_list.add(self.player)

        self.font = pygame.font.SysFont('Calibri', 25, True, False)

        # Open file to save timings
        self.results_file = open(RESULTS_FILE, "w")

    def add_coins(self):

        # Create the coins
        for i in range(COIN_COUNT_INCREMENT):
            # Create the coin instance
            # Coin image from kenney.nl
            coin = Coin()

            # Position the coin
            coin.rect.x = random.randrange(SPRITE_SIZE, SCREEN_WIDTH - SPRITE_SIZE)
            coin.rect.y = random.randrange(SPRITE_SIZE, SCREEN_HEIGHT - SPRITE_SIZE)

            # Add the coin to the lists
            self.coin_list.add(coin)

    def on_draw(self):
        """ Draw everything """

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        # Clear the screen
        self.screen.fill((59, 122, 87))

        # Draw all the spites
        self.coin_list.draw(self.screen)
        self.player_list.draw(self.screen)

        # Display timings
        output = f"Processing time: {self.processing_time:.3f}"
        text = self.font.render(output, True, BLACK)
        self.screen.blit(text, [20, SCREEN_HEIGHT - 40])

        output = f"Drawing time: {self.draw_time:.3f}"
        text = self.font.render(output, True, BLACK)
        self.screen.blit(text, [20, SCREEN_HEIGHT - 60])

        fps = self.fps.get_fps()
        output = f"FPS: {fps:3.0f}"
        text = self.font.render(output, True, BLACK)
        self.screen.blit(text, [20, SCREEN_HEIGHT - 80])

        pygame.display.flip()

        self.draw_time = timeit.default_timer() - draw_start_time
        self.fps.tick()

    def update(self, _delta_time):
        # Start update timer
        self.player_list.update()

        if self.player.rect.x < 0 and self.player.change_x < 0:
            self.player.change_x *= -1
        if self.player.rect.y < 0 and self.player.change_y < 0:
            self.player.change_y *= -1

        if self.player.rect.x > SCREEN_WIDTH and self.player.change_x > 0:
            self.player.change_x *= -1
        if self.player.rect.y > SCREEN_HEIGHT and self.player.change_y > 0:
            self.player.change_y *= -1

        start_time = timeit.default_timer()

        coin_hit_list = pygame.sprite.spritecollide(self.player, self.coin_list, False)
        for coin in coin_hit_list:
            coin.rect.x = random.randrange(SCREEN_WIDTH)
            coin.rect.y = random.randrange(SCREEN_HEIGHT)

        # Save the time it took to do this.
        self.processing_time = timeit.default_timer() - start_time

        # Total time program has been running
        total_program_time = int(timeit.default_timer() - self.program_start_time)

        # Print out stats, or add more sprites
        if total_program_time > self.last_fps_reading:
            self.last_fps_reading = total_program_time

            # It takes the program a while to "warm up", so the first
            # few seconds our readings will be off. So wait some time
            # before taking readings
            if total_program_time > 5:

                # We want the program to run for a while before taking
                # timing measurements. We don't want the time it takes
                # to add new sprites to be part of that measurement. So
                # make sure we have a clear second of nothing but
                # running the sprites, and not adding the sprites.
                if total_program_time % 2 == 1:

                    # Take timings
                    output = f"{total_program_time}, {len(self.coin_list)}, {self.fps.get_fps():.1f}, " \
                             f"{self.processing_time:.4f}, {self.draw_time:.4f}\n"
                    print(output, end="")
                    self.results_file.write(output)

                    if len(self.coin_list) >= STOP_COUNT:
                        pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
                        return

                    self.sprite_count_list.append(len(self.coin_list))
                    self.fps_list.append(round(self.fps.get_fps(), 1))
                    self.processing_time_list.append(self.processing_time)
                    self.drawing_time_list.append(self.draw_time)

                    # Now add the coins
                    self.add_coins()


def main():
    """ Main function """
    window = MyGame()

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        window.update(0)
        window.on_draw()
        clock.tick(60)

    pygame.quit()


main()
