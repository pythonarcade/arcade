"""
Eventually this will be an example showing how we support z-ordering.
"""
import arcade

SCALE = 0.75

SCREEN_HEIGHT = 320
SCREEN_WIDTH = 512


class MyApplication(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height):
        """ Set up the game and initialize the variables. """

        super().__init__(width, height)

        # Sprite lists
        self.all_sprites_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player_sprite = arcade.Sprite("examples/images/playerShip1_orange.png", SCALE)
        self.player_sprite.center_x = 200
        self.player_sprite.center_y = 200
        self.all_sprites_list.append(self.player_sprite)

        # Make the asteroids
        enemy_sprite = arcade.Sprite("examples/images/meteorGrey_big1.png", SCALE)
        enemy_sprite.center_y = 200
        enemy_sprite.center_x =  150
        enemy_sprite.size = 4
        self.all_sprites_list.append(enemy_sprite)

        enemy_sprite = arcade.Sprite("examples/images/meteorGrey_big2.png", SCALE)
        enemy_sprite.center_y = 200
        enemy_sprite.center_x =  250
        enemy_sprite.size = 4
        self.all_sprites_list.append(enemy_sprite)

        enemy_sprite = arcade.Sprite("examples/images/meteorGrey_big3.png", SCALE)
        enemy_sprite.center_y = 150
        enemy_sprite.center_x = 200
        enemy_sprite.size = 4
        self.all_sprites_list.append(enemy_sprite)

        self.background = arcade.load_texture("stars.jpg")

    def on_draw(self):
        """
        Render the screen.
        """

        # Draw the background
        arcade.draw_xywh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

        # Draw all the sprites.
        self.all_sprites_list.draw()



window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)
arcade.run()
