import arcade
import timeit

BALL_DRAG = 0.001
NO_FLIPPER = 0
FLIPPER_UP = 1


class MyApplication(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, resizable):
        super().__init__(width, height, resizable=resizable)
        self.sprite_list = arcade.SpriteList()

        self.left_flipper_list = arcade.SpriteList()
        self.right_flipper_list = arcade.SpriteList()
        self.left_flipper_state = NO_FLIPPER
        self.right_flipper_state = NO_FLIPPER

        self.time = 0
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # Top wall
        for x in range(20, 800, 40):
            wall = arcade.PhysicsAABB("images/boxCrate_double.png", [x, 980], [40, 40], [0, 0], 1, 100, 0)
            wall.static = True
            self.sprite_list.append(wall)

        # Left wall
        for y in range(260, 980, 40):
            wall = arcade.PhysicsAABB("images/boxCrate_double.png", [20, y], [40, 40], [0, 0], 1, 100, 0)
            wall.static = True
            self.sprite_list.append(wall)

        # Right wall
        for y in range(260, 980, 40):
            wall = arcade.PhysicsAABB("images/boxCrate_double.png", [780, y], [40, 40], [0, 0], 1, 100, 0)
            wall.static = True
            self.sprite_list.append(wall)

        # Left bottom slope
        y = 260
        for x in range(40, 280, 10):
            y -= 5
            wall = arcade.PhysicsAABB("images/boxCrate_double.png", [x, y], [10, 10], [0, 0], 1, 100, 0)
            wall.static = True
            self.sprite_list.append(wall)

        # Right bottom slope
        y = 260
        for x in range(760, 520, -10):
            y -= 5
            wall = arcade.PhysicsAABB("images/boxCrate_double.png", [x, y], [10, 10], [0, 0], 1, 100, 0)
            wall.static = True
            self.sprite_list.append(wall)

        # Left flipper
        y = 135
        for x in range(280, 350, 10):
            wall = arcade.PhysicsAABB("images/boxCrate_double.png", [x, y], [10, 10], [0, 0], 1, 100, 0)
            wall.static = True
            self.sprite_list.append(wall)
            self.left_flipper_list.append(wall)
            y -= 5

        # Right flipper
        y = 135
        for x in range(520, 440, -10):
            wall = arcade.PhysicsAABB("images/boxCrate_double.png", [x, y], [10, 10], [0, 0], 1, 100, 0)
            wall.static = True
            self.sprite_list.append(wall)
            self.right_flipper_list.append(wall)
            y -= 5

        # Bumpers
        for row in range(2):
            for column in range(2):
                bumper = arcade.PhysicsCircle("images/bumper.png", [250 + 300 * column, 450 + 300 * row], 35, [0, 0], 1.5, 100, BALL_DRAG)
                bumper.static = True
                self.sprite_list.append(bumper)

        wall = arcade.PhysicsAABB("images/python_logo.png", [400, 600], [150, 150], [0, 0], 1, 100, 0)
        wall.static = True
        self.sprite_list.append(wall)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()
        self.sprite_list.draw()
        start_x = 20
        start_y = 10
        arcade.draw_text("Processing time: {:.3f}".format(self.time), start_x, start_y, arcade.color.BLACK, 12)

    def update(self, x):
        """ Move everything """

        start_time = timeit.default_timer()

        arcade.process_2d_physics_movement(self.sprite_list, gravity=0.08)
        arcade.process_2d_physics_collisions(self.sprite_list)

        # -- Left flipper control
        if self.left_flipper_state == FLIPPER_UP and self.left_flipper_list[0].center_y < 145:
            y = 2
            y_change = 2
            for sprite in self.left_flipper_list:
                sprite.change_y = y
                y += y_change
                sprite.frozen = False
        elif self.left_flipper_state == NO_FLIPPER and self.left_flipper_list[0].center_y > 135:
            y = -2
            y_change = -2
            for sprite in self.left_flipper_list:
                sprite.change_y = y
                y += y_change
                sprite.frozen = False
        else:
            for sprite in self.left_flipper_list:
                sprite.change_y = 0
                sprite.frozen = True

        # -- Right flipper control
        if self.right_flipper_state == FLIPPER_UP and self.right_flipper_list[0].center_y < 145:
            y = 2
            y_change = 2
            for sprite in self.right_flipper_list:
                sprite.change_y = y
                y += y_change
                sprite.frozen = False
        elif self.right_flipper_state == NO_FLIPPER and self.right_flipper_list[0].center_y > 135:
            y = -2
            y_change = -2
            for sprite in self.right_flipper_list:
                sprite.change_y = y
                y += y_change
                sprite.frozen = False
        else:
            for sprite in self.right_flipper_list:
                sprite.change_y = 0
                sprite.frozen = True

        for sprite in self.sprite_list:
            if sprite.center_y < -20:
                sprite.kill()

        self.time = timeit.default_timer() - start_time


    def on_key_press(self, key, modifiers):
        """
        Called whenever the mouse moves.
        """

        if key == arcade.key.LEFT:
            self.left_flipper_state = FLIPPER_UP

        elif key == arcade.key.RIGHT:
            self.right_flipper_state = FLIPPER_UP

        elif key == arcade.key.SPACE:
            x = 720
            y = 300
            ball = arcade.PhysicsCircle("images/pool_cue_ball.png", [x, y], 15, [0, +20], 1, .25, BALL_DRAG)
            self.sprite_list.append(ball)

    def on_key_release(self, key, modifiers):
        """
        Called when the user presses a mouse button.
        """
        if key == arcade.key.LEFT:
            self.left_flipper_state = NO_FLIPPER

        elif key == arcade.key.RIGHT:
            self.right_flipper_state = NO_FLIPPER

window = MyApplication(800, 1000, resizable=False)
window.set_size(700, 700)
arcade.run()
