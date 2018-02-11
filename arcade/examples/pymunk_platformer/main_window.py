"""
Use Pymunk physics engine.

For more info on Pymunk see:
http://www.pymunk.org/en/latest/

To install pymunk:
pip install pymunk

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.pymunk_box_stacks

Click and drag with the mouse to move the boxes.
"""

import arcade
import pymunk
import timeit
import os

from constants import *
from physics_utility import *
from create_level import create_level_1

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height):
        super().__init__(width, height)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # -- Pymunk
        self.space = pymunk.Space()
        self.space.gravity = GRAVITY

        # Lists of sprites or lines
        self.dynamic_sprite_list = arcade.SpriteList()
        self.static_sprite_list = arcade.SpriteList()

        # Used for dragging shapes around with the mouse
        self.shape_being_dragged = None
        self.last_mouse_position = 0, 0

        self.draw_time = 0
        self.processing_time = 0

        self.force = (0, 0)

        # Set the viewport boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = 0
        self.view_bottom = 0

        create_level_1(self.space, self.static_sprite_list, self.dynamic_sprite_list)

        # Create player
        x = 50
        y = (SPRITE_SIZE + SPRITE_SIZE / 2)
        self.player = PymunkSprite("../images/character.png", x, y, scale=0.5, moment=pymunk.inf, mass=1)
        self.dynamic_sprite_list.append(self.player)
        self.space.add(self.player.body, self.player.shape)


    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        # Draw all the sprites
        self.static_sprite_list.draw()
        self.dynamic_sprite_list.draw()

        # Display timings
        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output, 20 + self.view_left, SCREEN_HEIGHT - 20 + self.view_bottom, arcade.color.WHITE, 12)

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, 20 + self.view_left, SCREEN_HEIGHT - 40 + self.view_bottom, arcade.color.WHITE, 12)

        self.draw_time = timeit.default_timer() - draw_start_time

    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1:
            self.last_mouse_position = (x + self.view_left, y + self.view_bottom)
            # See if we clicked on anything
            shape_list = self.space.point_query(self.last_mouse_position, 1, pymunk.ShapeFilter())

            # If we did, remember what we clicked on
            if len(shape_list) > 0:
                self.shape_being_dragged = shape_list[0]


    def on_mouse_release(self, x, y, button, modifiers):
        if button == 1:
            # Release the item we are holding (if any)
            self.shape_being_dragged = None

    def on_mouse_motion(self, x, y, dx, dy):
        if self.shape_being_dragged is not None:
            # If we are holding an object, move it with the mouse
            self.last_mouse_position =  (x + self.view_left, y + self.view_bottom)
            self.shape_being_dragged.shape.body.position = self.last_mouse_position
            self.shape_being_dragged.shape.body.velocity = dx * 20, dy * 20

    def scroll_viewport(self):
        # --- Manage Scrolling ---

        # Track if we need to change the viewport

        changed = False

        # Scroll left
        left_bndry = self.view_left + VIEWPORT_MARGIN
        if self.player.left < left_bndry:
            self.view_left -= left_bndry - self.player.left
            changed = True

        # Scroll right
        right_bndry = self.view_left + SCREEN_WIDTH - VIEWPORT_MARGIN
        if self.player.right > right_bndry:
            self.view_left += self.player.right - right_bndry
            changed = True

        # Scroll up
        top_bndry = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN
        if self.player.top > top_bndry:
            self.view_bottom += self.player.top - top_bndry
            changed = True

        # Scroll down
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN
        if self.player.bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.player.bottom
            changed = True

        if changed:
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


    def update(self, delta_time):
        start_time = timeit.default_timer()

        self.player.body.apply_force_at_local_point(self.force, (0, 0))

        check_collision(self.player)

        grounding = check_grounding(self.player)
        if self.force[0] and grounding and grounding['body']:
            grounding['body'].apply_force_at_world_point((-self.force[0],0), grounding['position'])

        # Check for balls that fall off the screen
        for sprite in self.dynamic_sprite_list:
            if sprite.shape.body.position.y < 0:
                # Remove balls from physics space
                self.space.remove(sprite.shape, sprite.shape.body)
                # Remove balls from physics list
                sprite.kill()

        # Update physics
        self.space.step(delta_time)

        # If we are dragging an object, make sure it stays with the mouse. Otherwise
        # gravity will drag it down.
        if self.shape_being_dragged is not None:
            self.shape_being_dragged.shape.body.position = self.last_mouse_position
            self.shape_being_dragged.shape.body.velocity = 0, 0

        resync_physics_sprites(self.dynamic_sprite_list)

        self.scroll_viewport()

        # Save the time it took to do this.
        self.processing_time = timeit.default_timer() - start_time



    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.RIGHT:
            self.force = (PLAYER_MOVE_FORCE, 0)
            self.player.shape.friction = 0
        elif symbol == arcade.key.LEFT:
            self.force = (-PLAYER_MOVE_FORCE, 0)
            self.player.shape.friction = 0
        elif symbol == arcade.key.UP:
            # find out if player is standing on ground
            grounding = check_grounding(self.player)
            if grounding['body'] != None and abs(grounding['normal'].x / grounding['normal'].y) < self.player.shape.friction:
                self.player.body.apply_impulse_at_local_point((0, PLAYER_JUMP_IMPULSE))

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.RIGHT:
            self.force = (0, 0)
            self.player.shape.friction = 15
        elif symbol == arcade.key.LEFT:
            self.force = (0, 0)
            self.player.shape.friction = 15


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)

    arcade.run()


if __name__ == "__main__":
    main()
