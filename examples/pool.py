import arcade
import timeit

BALL_DRAG = 0.02

class MyApplication(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height):
        super().__init__(width, height)
        self.object_list = arcade.SpriteList()
        self.time = 0
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.player = arcade.PhysicsCircle("images/pool_cue_ball.png", [390, 400], 15, [0, 0], 1, 1, BALL_DRAG)
        self.object_list.append(self.player)

        for row in range(5):
            for column in range(row + 1):
                x = 500 - row * 15 + column * 30
                y = 500 + row * 15 * 2
                ball = arcade.PhysicsCircle("images/pool_cue_ball.png", [x, y], 15, [0, 0], 1, 1, BALL_DRAG)
                self.object_list.append(ball)

        for x in range(200, 800, 40):
            wall = arcade.PhysicsAABB("images/boxCrate_double.png", [x, 700], [40, 40], [0, 0], 1, 100, BALL_DRAG)
            wall.static = True
            self.object_list.append(wall)

        for y in range(100, 700, 40):
            wall = arcade.PhysicsAABB("images/boxCrate_double.png", [200, y], [40, 40], [0, 0], 1, 100, BALL_DRAG)
            wall.static = True
            self.object_list.append(wall)

        for y in range(100, 700, 40):
            wall = arcade.PhysicsAABB("images/boxCrate_double.png", [760, y], [40, 40], [0, 0], 1, 100, BALL_DRAG)
            wall.static = True
            self.object_list.append(wall)

        for x in range(200, 800, 40):
            wall = arcade.PhysicsAABB("images/boxCrate_double.png", [x, 60], [40, 40], [0, 0], 1, 100, BALL_DRAG)
            wall.static = True
            self.object_list.append(wall)


    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()
        self.object_list.draw()
        start_x = 20
        start_y = 10
        arcade.draw_text("Processing time: {:.3f}".format(self.time), start_x, start_y, arcade.color.BLACK, 12)

    def animate(self, x):
        """ Move everything """

        start_time = timeit.default_timer()

        arcade.process_2d_physics_movement(self.object_list)
        arcade.process_2d_physics_collisions(self.object_list)
        self.player.velocity = [0, 0]

        self.time = timeit.default_timer() - start_time

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Called whenever the mouse moves.
        """
        self.player.velocity = [dx, dy]

        if self.player.position[0] + dx != x:
            self.player.position[0] = x - dx
        if self.player.position[1] + dy != y:
            self.player.position[1] = y - dy


window = MyApplication(1024, 800)

arcade.run()
