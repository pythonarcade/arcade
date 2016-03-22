"""
Example "Arcade" library code.

This example shows how to use functions to draw a scene.
"""

# Library imports
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def draw_background():
    """
    This function draws the background. Specifically, the sky and ground.
    """
    # Draw the sky in the top two-thirds
    arcade.draw_rect_filled(0, SCREEN_HEIGHT - 1,
                            SCREEN_WIDTH - 1, SCREEN_HEIGHT * 2 / 3,
                            arcade.color.SKY_BLUE)

    # Draw the ground in the bottom third
    arcade.draw_rect_filled(0, SCREEN_HEIGHT / 3,
                            SCREEN_WIDTH - 1, SCREEN_HEIGHT / 3,
                            arcade.color.DARK_SPRING_GREEN)


def draw_bird(x, y):
    """
    Draw a bird using a couple arcs.
    """
    arcade.draw_arc_outline(x, y, 20, 20, arcade.color.BLACK, 0, 90)
    arcade.draw_arc_outline(x + 40, y, 20, 20, arcade.color.BLACK, 90, 180)


def draw_pine_tree(x, y):
    """
    This function draws a pine tree at the specified location.
    """
    # Draw the trunk
    arcade.draw_rect_filled(x + 30, y - 100, 20, 40, arcade.color.DARK_BROWN)

    # Draw the triangle on top of the trunk
    point_list = ((x + 40, y),
                  (x, y - 100),
                  (x + 80, y - 100))

    arcade.draw_polygon_filled(point_list, arcade.color.DARK_GREEN)


def main():
    """
    This is the main program.
    """

    # Open the window
    arcade.open_window("Drawing With Functions", 600, 600)

    # Start the render process. This must be done before any drawing commands.
    arcade.start_render()

    # Call our drawing functions.
    draw_background()
    draw_pine_tree(50, 250)
    draw_pine_tree(350, 320)
    draw_bird(70, 500)
    draw_bird(470, 550)

    # Finish the render.
    # Nothing will be drawn without this.
    # Must happen after all draw commands
    arcade.finish_render()

    # Keep the window up until someone closes it.
    arcade.run()

if __name__ == "__main__":
    main()
