"""
Push a Sprite Out of Walls

Move the player with the arrow keys. It isn't stopped by a physics engine;
instead, after each move, any walls it overlaps push it back out using
arcade.get_collision_info_with_list(). Pushing out along the smallest
overlap lets the player slide along walls, including the rotated ones.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_push_out
"""

import arcade

SPRITE_SCALING = 0.5

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Push a Sprite Out of Walls Example"

MOVEMENT_SPEED = 5

# A sprite can overlap more than one wall. Pushing it out of one can push
# it into another, so try a few times.
MAX_PUSHES = 4


class GameView(arcade.View):
    """Main application class."""

    def __init__(self):
        super().__init__()

        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=SPRITE_SCALING,
        )
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        self.wall_list = arcade.SpriteList()

        self.background_color = arcade.color.AMAZON

    def setup(self):
        """Set up the game and initialize the variables."""
        self.player_sprite.position = 200, 300

        self.wall_list.clear()
        wall_texture = ":resources:images/tiles/boxCrate_double.png"

        # The walls of a room
        for x in range(96, 1200, 64):
            self.wall_list.append(
                arcade.Sprite(wall_texture, scale=SPRITE_SCALING, center_x=x, center_y=96)
            )
            self.wall_list.append(
                arcade.Sprite(wall_texture, scale=SPRITE_SCALING, center_x=x, center_y=608)
            )
        for y in range(160, 608, 64):
            self.wall_list.append(
                arcade.Sprite(wall_texture, scale=SPRITE_SCALING, center_x=96, center_y=y)
            )
            self.wall_list.append(
                arcade.Sprite(wall_texture, scale=SPRITE_SCALING, center_x=1184, center_y=y)
            )

        # Rotated walls the player slides along instead of stopping at
        for x, y, angle in ((450, 380, 45), (800, 260, -30), (950, 420, 15)):
            self.wall_list.append(
                arcade.Sprite(
                    wall_texture,
                    scale=SPRITE_SCALING * 2,
                    center_x=x,
                    center_y=y,
                    angle=angle,
                )
            )

    def on_draw(self):
        """Render the screen."""
        self.clear()
        self.wall_list.draw()
        self.player_list.draw()

    def push_player_out_of_walls(self):
        """Move the player out of any walls it overlaps."""
        for _ in range(MAX_PUSHES):
            # Results are sorted with the deepest overlap first
            hits = arcade.get_collision_info_with_list(self.player_sprite, self.wall_list)
            if not hits:
                return
            _wall, info = hits[0]
            # Move the smallest distance that separates the player from this wall
            self.player_sprite.position += info.normal * info.depth

    def on_update(self, delta_time):
        """Movement and game logic"""
        self.player_sprite.update()
        self.push_player_out_of_walls()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if key == arcade.key.UP:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key in (arcade.key.UP, arcade.key.DOWN):
            self.player_sprite.change_y = 0
        elif key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player_sprite.change_x = 0


def main():
    """Main function"""
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game = GameView()
    game.setup()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
