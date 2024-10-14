"""
Move with a Sprite Animation

Simple program to show basic sprite usage.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_move_animation
"""
import arcade
import random

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Move with a Sprite Animation Example"

COIN_SCALE = 0.5
COIN_COUNT = 50
CHARACTER_SCALING = 1

# How fast to move, and how fast to run the animation
MOVEMENT_SPEED = 5
UPDATES_PER_FRAME = 5

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1


class PlayerCharacter(arcade.Sprite):
    def __init__(self, idle_texture_pair, walk_texture_pairs):
        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.idle_texture_pair = idle_texture_pair
        self.walk_textures = walk_texture_pairs

        # Adjust the collision box. Default includes too much empty space
        # side-to-side. Box is centered at sprite center, (0, 0)
        self.points = [[-22, -64], [22, -64], [22, 28], [-22, 28]]
        # Set up parent class
        super().__init__(self.idle_texture_pair[0], scale=CHARACTER_SCALING)


    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Idle animation
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 7 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // UPDATES_PER_FRAME
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        """ Set up the game and initialize the variables. """
        super().__init__()

        # Sprite lists
        self.player_list = None
        self.coin_list = None

        # Set up the player
        self.score = 0
        self.score_text = arcade.Text("Score: 0", 10, 20, arcade.color.WHITE, 14)
        self.player = None

        # --- Load Textures for the player ---
        # Images from Kenney.nl's Asset Pack 3. We pick one randomly
        character_types = [
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer",
            ":resources:images/animated_characters/female_person/femalePerson",
            ":resources:images/animated_characters/male_person/malePerson",
            ":resources:images/animated_characters/male_adventurer/maleAdventurer",
            ":resources:images/animated_characters/zombie/zombie",
            ":resources:images/animated_characters/robot/robot",
        ]
        chosen_character = random.choice(character_types)

        # Load textures for idle standing
        idle_texture = arcade.load_texture(f"{chosen_character}_idle.png")
        self.idle_texture_pair = idle_texture, idle_texture.flip_left_right()

        # Load textures for walking
        self.walk_texture_pairs = []
        for i in range(8):
            texture = arcade.load_texture(f"{chosen_character}_walk{i}.png")
            self.walk_texture_pairs.append((texture, texture.flip_left_right()))

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player = PlayerCharacter(self.idle_texture_pair, self.walk_texture_pairs)
        self.player.position = self.center
        self.player.scale = 0.8

        self.player_list.append(self.player)

        for i in range(COIN_COUNT):
            coin = arcade.Sprite(":resources:images/items/gold_1.png", scale=0.5)
            coin.center_x = random.randrange(WINDOW_WIDTH)
            coin.center_y = random.randrange(WINDOW_HEIGHT)

            self.coin_list.append(coin)

        # Set the background color
        self.background_color = arcade.color.AMAZON

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.coin_list.draw()
        self.player_list.draw()

        # Put the text on the screen.
        self.score_text.text = f"Score: {self.score}"
        self.score_text.draw()

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed.
        """
        # Player controls for movement using arrow keys and WASD
        if key in (arcade.key.UP, arcade.key.W):
            self.player.change_y = MOVEMENT_SPEED
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.player.change_y = -MOVEMENT_SPEED
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.player.change_x = -MOVEMENT_SPEED
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.player.change_x = MOVEMENT_SPEED
        # Quit
        elif key in (arcade.key.ESCAPE, arcade.key.Q):
            arcade.close_window()

    def on_key_release(self, key, modifiers):
        """
        Called when the user releases a key.
        """
        if key in (arcade.key.UP, arcade.key.DOWN, arcade.key.W, arcade.key.S):
            self.player.change_y = 0
        elif key in (arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D):
            self.player.change_x = 0

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Move the player
        self.player_list.update()

        # Update the players animation
        self.player_list.update_animation()

        # Generate a list of all sprites that collided with the player.
        hit_list = arcade.check_for_collision_with_list(self.player, self.coin_list)

        # Loop through each colliding sprite, remove it, and add to the score.
        for coin in hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create and setup the GameView
    game = GameView()
    game.setup()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
