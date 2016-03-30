""" Bounce a ball on the screen, using gravity. """

import arcade

# Set up the constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Size of the circle.
CIRCLE_RADIUS = 20

# How strong the gravity is.
GRAVITY_CONSTANT = 0.3

# Percent of velocity maintained on a bounce.
BOUNCINESS = 0.9


def draw(dt):
    """ Use this function to draw everything to the screen. """

    # Start the render. This must happen before any drawing
    # commands. We do NOT need an stop render command.
    arcade.start_render()

    # Draw our rectangle
    arcade.draw_circle_filled(draw.x, draw.y, CIRCLE_RADIUS,
                              arcade.color.BLACK)

    # Modify rectangles position based on the delta
    # vector. (Delta means change. You can also think
    # of this as our speed and direction.)
    draw.x += draw.delta_x
    draw.y += draw.delta_y

    draw.delta_y -= GRAVITY_CONSTANT

    # Figure out if we hit the left or right edge and need to reverse.
    if draw.x < CIRCLE_RADIUS and draw.delta_x < 0:
        draw.delta_x *= -BOUNCINESS
    elif draw.x > SCREEN_WIDTH - CIRCLE_RADIUS and draw.delta_x > 0:
        draw.delta_x *= -BOUNCINESS

    # See if we hit the bottom
    if draw.y < CIRCLE_RADIUS and draw.delta_y < 0:
        # If we bounce with a decent velocity, do a normal bounce.
        # Otherwise we won't have enough time resolution to accurate represent
        # the bounce and it will bounce forever. So we'll divide the bounciness
        # by half to let it settle out.
        if draw.delta_y * -1 > GRAVITY_CONSTANT * 15:
            draw.delta_y *= -BOUNCINESS
        else:
            draw.delta_y *= -BOUNCINESS / 2

# These are function-specific variables. Before we
# use them in our function, we need to give them initial
# values.
draw.x = CIRCLE_RADIUS
draw.y = SCREEN_HEIGHT - CIRCLE_RADIUS
draw.delta_x = 2
draw.delta_y = 0

# Open up our window
arcade.open_window("Bouncing Ball", SCREEN_WIDTH, SCREEN_HEIGHT)
arcade.set_background_color(arcade.color.WHITE)

# Tell the computer to call the draw command at the specified interval.
arcade.schedule(draw, 1 / 80)

# Run the program
arcade.run()

# When done running the program, close the window.
arcade.close_window()
