"""
Section Example 2:

In this Section example we develop a very basic Pong game playable by two
persons in the same computer (hot seat!).

Each Player is abstracted as a Section that consists of a space in the screen
where the player paddle can move.

Note:
    - Sections can live along with Views. Sections do not need to occupy 100%
      of the screen.
    - View methods can interact with Sections by storing a reference to each
      one.
    - How keyboard events can be redirected to each section depending on the
      pressed key automatically.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sections_demo_2
"""

import random

import arcade
from arcade.color import BLACK, BLUE, RED, BEAU_BLUE, GRAY
from arcade.key import W, S, UP, DOWN

PLAYER_SECTION_WIDTH = 100
PLAYER_PADDLE_SPEED = 10


class Player(arcade.Section):
    """
    A Section representing the space in the screen where the player
    paddle can move
    """

    def __init__(
        self, left: int, bottom: int, width: int, height: int, key_up: int, key_down: int, **kwargs
    ):
        super().__init__(
            left,
            bottom,
            width,
            height,
            accept_keyboard_keys={key_up, key_down},
            **kwargs,
        )

        # keys assigned to move the paddle
        self.key_up: int = key_up
        self.key_down: int = key_down

        # the player paddle
        self.paddle: arcade.SpriteSolidColor = arcade.SpriteSolidColor(30, 100, color=BLACK)

        # player score
        self.score: int = 0

    def setup(self):
        # reset the player paddle position to the middle of the screen
        self.paddle.position = self.left + 50, self.height / 2

    def on_update(self, delta_time: float):
        # update the paddle position
        self.paddle.update()

    def on_draw(self):
        # draw sections info and score
        if self.name == "Left":
            keys = "W and S"
            start_x = self.left + 5
        else:
            keys = "UP and DOWN"
            start_x = self.left - 290
        arcade.draw_text(
            f"Player {self.name} (move paddle with: {keys})",
            start_x,
            self.top - 20,
            BLUE,
            9,
        )
        arcade.draw_text(
            f"Score: {self.score}",
            self.left + 20,
            self.bottom + 20,
            BLUE,
        )

        # draw the paddle
        arcade.draw_sprite(self.paddle)

    def on_key_press(self, symbol: int, modifiers: int):
        # set the paddle direction and movement speed
        if symbol == self.key_up:
            self.paddle.change_y = PLAYER_PADDLE_SPEED
        else:
            self.paddle.change_y = -PLAYER_PADDLE_SPEED

    def on_key_release(self, _symbol: int, _modifiers: int):
        # stop moving the paddle
        self.paddle.stop()


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        # a sprite list that will hold each player paddle to
        # check for collisions
        self.paddles: arcade.SpriteList = arcade.SpriteList()

        # we store each Section
        self.left_player: Player = Player(
            0, 0, PLAYER_SECTION_WIDTH, self.window.height, key_up=W, key_down=S, name="Left"
        )
        self.right_player: Player = Player(
            self.window.width - PLAYER_SECTION_WIDTH,
            0,
            PLAYER_SECTION_WIDTH,
            self.window.height,
            key_up=UP,
            key_down=DOWN,
            name="Right",
        )

        # add the sections to the SectionManager so Sections start to work
        self.section_manager = arcade.SectionManager(self)
        self.section_manager.add_section(self.left_player)
        self.section_manager.add_section(self.right_player)

        # add each paddle to the sprite list
        self.paddles.append(self.left_player.paddle)
        self.paddles.append(self.right_player.paddle)

        # create the ball
        self.ball: arcade.SpriteCircle = arcade.SpriteCircle(20, RED)

    def setup(self):
        # set up a new game

        # set ball position in the middle
        self.ball.position = self.window.width / 2, self.window.height / 2

        # randomize ball direction and speed
        self.ball.change_x = random.choice([-3, -2, 3, 2])
        self.ball.change_y = random.choice([-3, -2, 3, 2])

        # setup player paddles
        self.left_player.setup()
        self.right_player.setup()

    def on_show_view(self) -> None:
        self.section_manager.enable()

    def on_hide_view(self) -> None:
        self.section_manager.disable()

    def on_update(self, delta_time: float):
        self.ball.update()  # update the ball

        # bounce the ball either at the top or at the bottom
        if self.ball.bottom <= 0:
            self.ball.change_y *= -1
        elif self.ball.top >= self.window.height:
            self.ball.change_y *= -1

        # check if the ball has collided with a paddle
        collided_paddle = self.ball.collides_with_list(self.paddles)
        if collided_paddle:
            # adjust ball coordinates to simplify the game
            if collided_paddle[0] is self.left_player.paddle:
                self.ball.left = self.left_player.paddle.right
            else:
                self.ball.right = self.right_player.paddle.left

            # bounce the ball from the paddle
            self.ball.change_x *= -1

        # check if the ball has exited the screen in either side and
        # end the game
        if self.ball.right <= 0:
            self.end_game(self.right_player)
        elif self.ball.left >= self.window.width:
            self.end_game(self.left_player)

    def end_game(self, winner: Player):
        """Called when one player wins"""
        winner.score += 1  # increment the winner score
        self.setup()  # prepare a new game

    def on_draw(self):
        self.clear(color=BEAU_BLUE)  # clear the screen

        arcade.draw_sprite(self.ball)  # draw the ball

        half_window_x = self.window.width / 2  # middle x

        # draw a line diving the screen in half
        arcade.draw_line(half_window_x, 0, half_window_x, self.window.height, GRAY, 2)


def main():
    # create the window
    window = arcade.Window(title="Two player simple Pong with Sections!")

    # create the custom View
    game = GameView()
    game.setup()

    # show the view
    window.show_view(game)

    # run arcade loop
    window.run()


if __name__ == "__main__":
    main()
