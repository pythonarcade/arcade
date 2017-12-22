"""
Example "Arcade" library code.

This example shows how to use functions and loops to draw a scene.
It does not assume that the programmer knows how to use classes yet.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.drawing_with_loops
"""

# Library imports
import arcade
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600



def draw_background():
    """
    This function draws the background. Specifically, the sky and ground.
    """
    # Draw the sky in the top two-thirds
    arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 2 / 3,
                                 SCREEN_WIDTH - 1, SCREEN_HEIGHT * 2 / 3,
                                 arcade.color.SKY_BLUE)

    # Draw the ground in the bottom third
    arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 6,
                                 SCREEN_WIDTH - 1, SCREEN_HEIGHT / 3,
                                 arcade.color.DARK_SPRING_GREEN)


def draw_bird(x, y):
    """
    Draw a bird using a couple arcs.
    """
    arcade.draw_arc_outline(x, y, 20, 20, arcade.color.BLACK, 0, 90)
    arcade.draw_arc_outline(x + 40, y, 20, 20, arcade.color.BLACK, 90, 180)


def draw_pine_tree(center_x, center_y):
    """
    This function draws a pine tree at the specified location.

    Args:
      :center_x: x position of the tree center.
      :center_y: y position of the tree trunk center.
    """
    # Draw the trunkcenter_x
    arcade.draw_rectangle_filled(center_x, center_y, 20, 40, arcade.color.DARK_BROWN)

    tree_bottom_y = center_y + 20

    # Draw the triangle on top of the trunk
    point_list = ((center_x - 40, tree_bottom_y),
                  (center_x, tree_bottom_y + 100),
                  (center_x + 40, tree_bottom_y))

    arcade.draw_polygon_filled(point_list, arcade.color.DARK_GREEN)

def draw_birds():
    # Loop to draw ten birds in random locations.
    for bird in draw_birds.bird_list:

        # Draw the bird.
        draw_bird(bird[0], bird[1])

draw_birds.bird_list = []


def draw_trees():
    # Draw the top row of trees
    for x in range(45, SCREEN_WIDTH, 90):
        draw_pine_tree(x, SCREEN_HEIGHT / 3)

    # Draw the bottom row of trees
    for x in range(65, SCREEN_WIDTH, 90):
        draw_pine_tree(x, (SCREEN_HEIGHT / 3) - 120)


@arcade.decorator.init
def create_birds(window):
    for bird_count in range(10):
        x = random.randrange(SCREEN_WIDTH)
        y = random.randrange(SCREEN_HEIGHT / 2, SCREEN_HEIGHT)
        draw_birds.bird_list.append([x,y])

@arcade.decorator.animate
def animate_birds(delta_time):
    for bird in draw_birds.bird_list:
        bird[0] += 0.3
        if bird[0] > SCREEN_WIDTH + 20:
            bird[0] = -20

@arcade.decorator.draw
def draw():

    # Call our drawing functions.
    draw_background()
    draw_birds()
    draw_trees()


if __name__ == "__main__":
    arcade.decorator.run(SCREEN_WIDTH, SCREEN_HEIGHT, title="Drawing With Loops")

