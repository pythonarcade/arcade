"""
Example showing how to use the easing functions for position.
Example showing how to use easing for angles.

See:
https://easings.net/
...for a great guide on the theory behind how easings can work.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.easing_example_2
"""

import arcade
from arcade import easing

SPRITE_SCALING = 1.0

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Easing Example"


class Player(arcade.Sprite):
    """Player class"""

    def __init__(self, image, scale):
        """Set up the player"""

        # Call the parent init
        super().__init__(image, scale=scale)

        self.easing_angle_data = None
        self.easing_x_data = None
        self.easing_y_data = None

    def update(self, delta_time: float = 1 / 60):
        if self.easing_angle_data is not None:
            done, self.angle = easing.ease_angle_update(self.easing_angle_data, delta_time)
            if done:
                self.easing_angle_data = None

        if self.easing_x_data is not None:
            done, self.center_x = easing.ease_update(self.easing_x_data, delta_time)
            if done:
                self.easing_x_data = None

        if self.easing_y_data is not None:
            done, self.center_y = easing.ease_update(self.easing_y_data, delta_time)
            if done:
                self.easing_y_data = None


class GameView(arcade.View):
    """Main application class."""

    def __init__(self):
        """Initializer"""

        # Call the parent class initializer
        super().__init__()

        # Set up the player info
        self.player_list = arcade.SpriteList()

        # Load the player texture. The ship points up by default. We need it to point right.
        # That's why we rotate it 90 degrees clockwise.
        texture = arcade.load_texture(":resources:images/space_shooter/playerShip1_orange.png")
        texture = texture.rotate_90()

        # Set up the player
        self.player_sprite = Player(texture, SPRITE_SCALING)
        self.player_sprite.angle = 0
        self.player_sprite.center_x = WINDOW_WIDTH / 2
        self.player_sprite.center_y = WINDOW_HEIGHT / 2
        self.player_list.append(self.player_sprite)

        # Set the background color
        self.background_color = arcade.color.BLACK
        self.text = "Move the mouse and press 1-9 to apply an easing function."

    def on_draw(self):
        """Render the screen."""

        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.player_list.draw()

        arcade.draw_text(self.text, 15, 15, arcade.color.WHITE, 24)

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.player_list.update(delta_time)

    def on_key_press(self, key, modifiers):
        x = self.window.mouse["x"]
        y = self.window.mouse["y"]

        if key == arcade.key.KEY_1:
            angle = arcade.math.get_angle_degrees(
                x1=self.player_sprite.position[0], y1=self.player_sprite.position[1], x2=x, y2=y
            )
            self.player_sprite.angle = angle
            self.text = "Instant angle change"
        if key in [arcade.key.KEY_2, arcade.key.KEY_3, arcade.key.KEY_4, arcade.key.KEY_5]:
            p1 = self.player_sprite.position
            p2 = (x, y)
            end_angle = arcade.math.get_angle_degrees(p1[0], p1[1], p2[0], p2[1])
            start_angle = self.player_sprite.angle
            if key == arcade.key.KEY_2:
                ease_function = easing.linear
                self.text = "Linear easing - angle"
            elif key == arcade.key.KEY_3:
                ease_function = easing.ease_in
                self.text = "Ease in - angle"
            elif key == arcade.key.KEY_4:
                ease_function = easing.ease_out
                self.text = "Ease out - angle"
            elif key == arcade.key.KEY_5:
                ease_function = easing.smoothstep
                self.text = "Smoothstep - angle"
            else:
                raise ValueError("?")

            self.player_sprite.easing_angle_data = easing.ease_angle(
                start_angle, end_angle, rate=180, ease_function=ease_function
            )

        if key in [arcade.key.KEY_6, arcade.key.KEY_7, arcade.key.KEY_8, arcade.key.KEY_9]:
            p1 = self.player_sprite.position
            p2 = (x, y)
            if key == arcade.key.KEY_6:
                ease_function = easing.linear
                self.text = "Linear easing - position"
            elif key == arcade.key.KEY_7:
                ease_function = easing.ease_in
                self.text = "Ease in - position"
            elif key == arcade.key.KEY_8:
                ease_function = easing.ease_out
                self.text = "Ease out - position"
            elif key == arcade.key.KEY_9:
                ease_function = easing.smoothstep
                self.text = "Smoothstep - position"
            else:
                raise ValueError("?")

            ex, ey = easing.ease_position(p1, p2, rate=180, ease_function=ease_function)
            self.player_sprite.easing_x_data = ex
            self.player_sprite.easing_y_data = ey

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        angle = arcade.math.get_angle_degrees(
            x1=self.player_sprite.position[0], y1=self.player_sprite.position[1], x2=x, y2=y
        )
        self.player_sprite.angle = angle


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
