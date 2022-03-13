import arcade

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Easing Example"

X_START = 30
X_END = 770
Y_INTERVAL = 50
BALL_SIZE = 13


class Player(arcade.Sprite):
    """ Player class """

    def __init__(self, image, scale):
        """ Set up the player """

        # Call the parent init
        super().__init__(image, scale)

        self.easing_x_data = None
        self.easing_y_data = None

    def on_update(self, delta_time: float = 1 / 60):

        if self.easing_x_data is not None:
            done, self.center_x = arcade.ease_update(self.easing_x_data, delta_time)
            if done:
                self.easing_x_data = None

        if self.easing_y_data is not None:
            done, self.center_y = arcade.ease_update(self.easing_y_data, delta_time)
            if done:
                self.easing_y_data = None


class EasingCircle(arcade.SpriteCircle):
    """ Player class """

    def __init__(self, radius, color):
        """ Set up the player """

        # Call the parent init
        super().__init__(radius, color)

        self.easing_x_data = None
        self.easing_y_data = None

    def on_update(self, delta_time: float = 1 / 60):
        if self.easing_x_data is not None:
            done, self.center_x = arcade.ease_update(self.easing_x_data, delta_time)
            if done:
                x = X_START
                if self.center_x < SCREEN_WIDTH / 2:
                    x = X_END
                ex, ey = arcade.ease_position(self.position,
                                              (x, self.center_y),
                                              rate=180,
                                              ease_function=self.easing_x_data.ease_function)
                self.easing_x_data = ex

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

        # Set the background color
        arcade.set_background_color(arcade.color.BLACK)

        self.ball_list = None
        self.text_list = []

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.ball_list = arcade.SpriteList()

        def create_ball(y, ease_function):
            ball = EasingCircle(BALL_SIZE, arcade.color.WHITE)
            ball.position = X_START, y
            p1 = ball.position
            p2 = (X_END, y)
            ex, ey = arcade.ease_position(p1, p2, rate=180, ease_function=ease_function)
            ball.ease_function = ease_function
            ball.easing_x_data = ex
            ball.easing_y_data = ey
            return ball

        y = Y_INTERVAL
        ball = create_ball(y, arcade.linear)
        self.ball_list.append(ball)
        text = arcade.Text("Linear", X_START, y, color=arcade.color.WHITE)
        self.text_list.append(text)

        y += Y_INTERVAL
        ball = create_ball(y, arcade.ease_out)
        self.ball_list.append(ball)
        text = arcade.Text("Ease out", X_START, y, color=arcade.color.WHITE)
        self.text_list.append(text)

        y += Y_INTERVAL
        ball = create_ball(y, arcade.ease_in)
        self.ball_list.append(ball)
        text = arcade.Text("Ease in", X_START, y, color=arcade.color.WHITE)
        self.text_list.append(text)

        y += Y_INTERVAL
        ball = create_ball(y, arcade.smoothstep)
        self.ball_list.append(ball)
        text = arcade.Text("Smoothstep", X_START, y, color=arcade.color.WHITE)
        self.text_list.append(text)

        y += Y_INTERVAL
        ball = create_ball(y, arcade.ease_in_out)
        self.ball_list.append(ball)
        text = arcade.Text("Ease in/out", X_START, y, color=arcade.color.WHITE)
        self.text_list.append(text)

        y += Y_INTERVAL
        ball = create_ball(y, arcade.ease_out_elastic)
        self.ball_list.append(ball)
        text = arcade.Text("Ease out elastic", X_START, y, color=arcade.color.WHITE)
        self.text_list.append(text)

        y += Y_INTERVAL
        ball = create_ball(y, arcade.ease_in_back)
        self.ball_list.append(ball)
        text = arcade.Text("Ease in back", X_START, y, color=arcade.color.WHITE)
        self.text_list.append(text)

        y += Y_INTERVAL
        ball = create_ball(y, arcade.ease_out_back)
        self.ball_list.append(ball)
        text = arcade.Text("Ease out back", X_START, y, color=arcade.color.WHITE)
        self.text_list.append(text)

        y += Y_INTERVAL
        ball = create_ball(y, arcade.ease_in_sin)
        self.ball_list.append(ball)
        text = arcade.Text("Ease in sin", X_START, y, color=arcade.color.WHITE)
        self.text_list.append(text)

        y += Y_INTERVAL
        ball = create_ball(y, arcade.ease_out_sin)
        self.ball_list.append(ball)
        text = arcade.Text("Ease out sin", X_START, y, color=arcade.color.WHITE)
        self.text_list.append(text)

        y += Y_INTERVAL
        ball = create_ball(y, arcade.ease_in_out_sin)
        self.ball_list.append(ball)
        text = arcade.Text("Ease in out sin", X_START, y, color=arcade.color.WHITE)
        self.text_list.append(text)

    def on_draw(self):
        """ Render the screen. """

        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        # self.player_list.draw()
        self.ball_list.draw()

        for text in self.text_list:
            text.draw()

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.ball_list.on_update(delta_time)


def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
