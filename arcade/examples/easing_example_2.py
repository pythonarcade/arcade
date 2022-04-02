import arcade

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Easing Example"


class Player(arcade.Sprite):
    """ Player class """

    def __init__(self, image, scale):
        """ Set up the player """

        # Call the parent init
        super().__init__(image, scale)

        self.easing_angle_data = None
        self.easing_x_data = None
        self.easing_y_data = None

    def on_update(self, delta_time: float = 1 / 60):
        if self.easing_angle_data is not None:
            done, self.angle = arcade.ease_angle_update(self.easing_angle_data, delta_time)
            if done:
                self.easing_angle_data = None

        if self.easing_x_data is not None:
            done, self.center_x = arcade.ease_update(self.easing_x_data, delta_time)
            if done:
                self.easing_x_data = None

        if self.easing_y_data is not None:
            done, self.center_y = arcade.ease_update(self.easing_y_data, delta_time)
            if done:
                self.easing_y_data = None


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        """ Initializer """

        # Call the parent class initializer
        super().__init__(width, height, title)

        # Variables that will hold sprite lists
        self.player_list = None

        # Set up the player info
        self.player_sprite = None

        # Set the background color
        self.background_color = arcade.color.BLACK
        self.text = "Test"

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player(":resources:images/space_shooter/playerShip1_orange.png",
                                    SPRITE_SCALING)
        self.player_sprite.angle = 0
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 2
        self.player_list.append(self.player_sprite)

    def on_draw(self):
        """ Render the screen. """

        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.player_list.draw()

        arcade.draw_text(self.text, 10, 10, arcade.color.WHITE, 18)

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.player_list.on_update(delta_time)

    def on_key_press(self, key, modifiers):
        x = self.mouse["x"]
        y = self.mouse["y"]

        if key == arcade.key.KEY_1:
            point = x, y
            self.player_sprite.face_point(point)
            self.text = "Instant angle change"
        if key in [arcade.key.KEY_2, arcade.key.KEY_3, arcade.key.KEY_4, arcade.key.KEY_5]:
            p1 = self.player_sprite.position
            p2 = (x, y)
            end_angle = -arcade.get_angle_degrees(p1[0], p1[1], p2[0], p2[1])
            start_angle = self.player_sprite.angle
            if key == arcade.key.KEY_2:
                ease_function = arcade.linear
                self.text = "Linear easing - angle"
            elif key == arcade.key.KEY_3:
                ease_function = arcade.ease_in
                self.text = "Ease in - angle"
            elif key == arcade.key.KEY_4:
                ease_function = arcade.ease_out
                self.text = "Ease out - angle"
            elif key == arcade.key.KEY_5:
                ease_function = arcade.smoothstep
                self.text = "Smoothstep - angle"
            else:
                raise ValueError("?")

            self.player_sprite.easing_angle_data = arcade.ease_angle(start_angle,
                                                                     end_angle,
                                                                     rate=180,
                                                                     ease_function=ease_function)

        if key in [arcade.key.KEY_6, arcade.key.KEY_7, arcade.key.KEY_8, arcade.key.KEY_9]:
            p1 = self.player_sprite.position
            p2 = (x, y)
            if key == arcade.key.KEY_6:
                ease_function = arcade.linear
                self.text = "Linear easing - position"
            elif key == arcade.key.KEY_7:
                ease_function = arcade.ease_in
                self.text = "Ease in - position"
            elif key == arcade.key.KEY_8:
                ease_function = arcade.ease_out
                self.text = "Ease out - position"
            elif key == arcade.key.KEY_9:
                ease_function = arcade.smoothstep
                self.text = "Smoothstep - position"
            else:
                raise ValueError("?")

            ex, ey = arcade.ease_position(p1, p2, rate=180, ease_function=ease_function)
            self.player_sprite.easing_x_data = ex
            self.player_sprite.easing_y_data = ey

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.player_sprite.face_point((x, y))


def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
