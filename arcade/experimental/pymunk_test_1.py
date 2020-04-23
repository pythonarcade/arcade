import arcade

SCREEN_TITLE = "Starting Template Simple"
SPRITE_SCALING_PLAYER = 0.5
MOVEMENT_SPEED = 5
PLAYER_MOVE_FORCE = 700

SPRITE_IMAGE_SIZE = 128
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

SCREEN_WIDTH = SPRITE_SIZE * 20
SCREEN_HEIGHT = SPRITE_SIZE * 15

from arcade.experimental.pymunk_physics_engine import PymunkPhysicsEngine

class MyWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

        self.player_list = None
        self.wall_list = None
        self.item_list = None
        self.player_sprite = None
        self.physics_engine = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

    def setup(self):
        # Create the sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.item_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png",
                                           SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = 250
        self.player_sprite.center_y = 250
        self.player_list.append(self.player_sprite)

        # Set up the walls
        for x in range(0, SCREEN_WIDTH + 1, SPRITE_SIZE):
            wall = arcade.Sprite(":resources:images/tiles/grassCenter.png",
                                 SPRITE_SCALING_PLAYER)
            wall.center_x = x
            wall.center_y = 0
            self.wall_list.append(wall)

            wall = arcade.Sprite(":resources:images/tiles/grassCenter.png",
                                 SPRITE_SCALING_PLAYER)
            wall.center_x = x
            wall.center_y = SCREEN_HEIGHT
            self.wall_list.append(wall)

        # Set up the walls
        for y in range(SPRITE_SIZE, SCREEN_HEIGHT, SPRITE_SIZE):
            wall = arcade.Sprite(":resources:images/tiles/grassCenter.png",
                                 SPRITE_SCALING_PLAYER)
            wall.center_x = 0
            wall.center_y = y
            self.wall_list.append(wall)

            wall = arcade.Sprite(":resources:images/tiles/grassCenter.png",
                                 SPRITE_SCALING_PLAYER)
            wall.center_x = SCREEN_WIDTH
            wall.center_y = y
            self.wall_list.append(wall)

        # Add some movable boxes
        for x in range(SPRITE_SIZE * 3, SPRITE_SIZE * 8, SPRITE_SIZE):
            item = arcade.Sprite(":resources:images/tiles/boxCrate.png",
                                 SPRITE_SCALING_PLAYER)
            item.center_x = x
            item.center_y = 400
            self.item_list.append(item)

        # Create the physics engine
        self.physics_engine = PymunkPhysicsEngine(damping=0.5)
        self.physics_engine.add_sprite(self.player_sprite, moment=PymunkPhysicsEngine.MOMENT_INF)

        self.physics_engine.add_sprite_list(self.wall_list,
                                            mass=1,
                                            friction=0,
                                            moment=None,
                                            body_type=PymunkPhysicsEngine.STATIC)

        self.physics_engine.add_sprite_list(self.item_list,
                                            mass=1,
                                            friction=0,
                                            moment=None,
                                            body_type=PymunkPhysicsEngine.DYNAMIC)


    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Calculate speed based on the keys pressed
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        if self.up_pressed and not self.down_pressed:
            force = (0, PLAYER_MOVE_FORCE)
            self.physics_engine.apply_force(self.player_sprite, force)
        elif self.down_pressed and not self.up_pressed:
            force = (0, -PLAYER_MOVE_FORCE)
            self.physics_engine.apply_force(self.player_sprite, force)
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -MOVEMENT_SPEED
            force = (-PLAYER_MOVE_FORCE, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
        elif self.right_pressed and not self.left_pressed:
            force = (PLAYER_MOVE_FORCE, 0)
            self.physics_engine.apply_force(self.player_sprite, force)

        self.physics_engine.step()
        self.physics_engine.resync_sprites()

    def on_draw(self):
        arcade.start_render()
        self.wall_list.draw()
        self.item_list.draw()
        self.player_list.draw()

def main():
    window = MyWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
