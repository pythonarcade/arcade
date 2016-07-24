import arcade
import timeit

MOVEMENT_SPEED = 1


def create_boxes(object_list, start_x, start_y, width, height):
    spacing = 20
    for x in range(start_x, start_x + width * spacing, spacing):
        for y in range(start_y, start_y + height * spacing, spacing):
            a = arcade.PhysicsAABB("images/boxCrate_double.png", [x, y], [15, 15], [0, 0], .4, 1, 0.25)
            object_list.append(a)


def create_circles(object_list, start_x, start_y, width, height):
    spacing = 20
    for x in range(start_x, start_x + width * spacing, spacing):
        for y in range(start_y, start_y + height * spacing, spacing):
            a = arcade.PhysicsCircle("images/coin_01.png", [x, y], 9, [0, 0], .1, 1, 0.15)
            object_list.append(a)


class MyApplication(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height):
        super().__init__(width, height)
        self.hit_sound = arcade.load_sound("sounds/rockHit2.ogg")
        self.object_list = arcade.SpriteList()
        self.time = 0
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.player = arcade.PhysicsAABB("images/character.png", [390, 400], [79 / 2, 125 / 2], [0, 0], .7, 3, 0.4)
        self.object_list.append(self.player)

        create_circles(self.object_list, 300, 300, 5, 2)

        a = arcade.PhysicsCircle("images/meteorGrey_med1.png", [400, 150], 20, [0, 0], .8, 2, 0.1)
        self.object_list.append(a)
        a = arcade.PhysicsCircle("images/meteorGrey_med2.png", [370, 120], 20, [0, 0], .8, 2, 0.1)
        self.object_list.append(a)
        a = arcade.PhysicsCircle("images/meteorGrey_med1.png", [430, 120], 20, [0, 0], .8, 2, 0.1)
        self.object_list.append(a)
        a = arcade.PhysicsCircle("images/meteorGrey_med1.png", [400, 90], 20, [0, 0], .8, 2, 0.1)
        self.object_list.append(a)

        create_boxes(self.object_list, 150, 250, 2, 20)
        create_boxes(self.object_list, 450, 250, 2, 20)
        create_boxes(self.object_list, 190, 250, 13, 2)
        create_boxes(self.object_list, 190, 450, 13, 2)
        create_boxes(self.object_list, 190, 610, 13, 2)

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

        self.time = timeit.default_timer() - start_time

    def on_key_press(self, key, modifiers):
        """
        Called whenever the mouse moves.
        """
        if key == arcade.key.UP:
            self.player.force[1] = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player.force[1] = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player.force[0] = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player.force[0] = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """
        Called when the user presses a mouse button.
        """
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player.force[1] = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player.force[0] = 0

window = MyApplication(1024, 800)

arcade.run()
