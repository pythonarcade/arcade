"""
Sprite Health Bars

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_health
"""
import math
import arcade

SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_ENEMY = 0.5
SPRITE_SCALING_BULLET = 1
INDICATOR_BAR_OFFSET = 32
ENEMY_ATTACK_COOLDOWN = 0.5
BULLET_SPEED = 5
BULLET_DAMAGE = 1
PLAYER_HEALTH = 10

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprite Health Bars"


class Player(arcade.Sprite):
    def __init__(self, filename: str, scale: float, bar_list: arcade.SpriteList) -> None:
        super().__init__(filename=filename, scale=scale)
        self.indicator_bar: IndicatorBar = IndicatorBar(self, bar_list, self.position)
        self.health: int = PLAYER_HEALTH


class IndicatorBar:
    """
    Represents a bar which can display information about a sprite.

    Parameters
    ----------
    owner: Player
        The owner of this indicator bar.
    sprite_list: arcade.SpriteList
        The sprite list used to draw the indicator bar components.
    position: tuple[float, float]
        The initial position of the bar.
    full_color: arcade.Color
        The color of the bar.
    background_color: arcade.Color
        The background color of the bar.
    width: int
        The width of the bar.
    height: int
        The height of the bar.
    border_size: int
        The size of the bar's border.
    """

    def __init__(
        self,
        owner: Player,
        sprite_list: arcade.SpriteList,
        position: tuple[float, float] = (0, 0),
        full_color: arcade.Color = arcade.color.GREEN,
        background_color: arcade.Color = arcade.color.BLACK,
        width: int = 100,
        height: int = 4,
        border_size: int = 4,
    ) -> None:
        # Store the reference to the owner and the sprite list
        self.owner: Player = owner
        self.sprite_list: arcade.SpriteList = sprite_list

        # Set the needed size variables
        self._box_width: int = width
        self._box_height: int = height
        self._half_box_width: int = self._box_width // 2
        self._center_x: float = 0.0
        self._center_y: float = 0.0
        self._fullness: float = 0.0

        # Create the boxes needed to represent the indicator bar
        self._background_box: arcade.SpriteSolidColor = arcade.SpriteSolidColor(
            self._box_width + border_size,
            self._box_height + border_size,
            background_color,
        )
        self._full_box: arcade.SpriteSolidColor = arcade.SpriteSolidColor(
            self._box_width,
            self._box_height,
            full_color,
        )
        self.sprite_list.append(self._background_box)
        self.sprite_list.append(self._full_box)

        # Set the fullness and position of the bar
        self.fullness: float = 1.0
        self.position: tuple[float, float] = position

    def __repr__(self) -> str:
        return f"<IndicatorBar (Owner={self.owner})>"

    @property
    def background_box(self) -> arcade.SpriteSolidColor:
        """Returns the background box of the indicator bar."""
        return self._background_box

    @property
    def full_box(self) -> arcade.SpriteSolidColor:
        """Returns the full box of the indicator bar."""
        return self._full_box

    @property
    def fullness(self) -> float:
        """Returns the fullness of the bar."""
        return self._fullness

    @fullness.setter
    def fullness(self, new_fullness: float) -> None:
        """Sets the fullness of the bar."""
        # Check if new_fullness if valid
        if not (0.0 <= new_fullness <= 1.0):
            raise ValueError(
                f"Got {new_fullness}, but fullness must be between 0.0 and 1.0."
            )

        # Set the size of the bar
        self._fullness = new_fullness
        if new_fullness == 0.0:
            # Set the full_box to not be visible since it is not full anymore
            self.full_box.visible = False
        else:
            # Set the full_box to be visible incase it wasn't then update the bar
            self.full_box.visible = True
            self.full_box.width = self._box_width * new_fullness
            self.full_box.left = self._center_x - (self._box_width // 2)

    @property
    def position(self) -> tuple[float, float]:
        """Returns the current position of the bar."""
        return self._center_x, self._center_y

    @position.setter
    def position(self, new_position: tuple[float, float]) -> None:
        """Sets the new position of the bar."""
        # Check if the position has changed. If so, change the bar's position
        if new_position != self.position:
            self._center_x, self._center_y = new_position
            self.background_box.position = new_position
            self.full_box.position = new_position

            # Make sure full_box is to the left of the bar instead of the middle
            self.full_box.left = self._center_x - (self._box_width // 2)


class MyGame(arcade.Window):
    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.player_sprite = None
        self.enemy_sprite = None
        self.bullet_list = None
        self.bar_list = None
        self.enemy_timer = 0

    def setup(self) -> None:
        """Set up the game and initialize the variables."""
        # Sprite lists
        self.bullet_list = arcade.SpriteList()
        self.bar_list = arcade.SpriteList()

        # Player and enemy
        self.player_sprite = Player(":resources:images/animated_characters/female_person/femalePerson_idle.png", SPRITE_SCALING_PLAYER, self.bar_list)
        self.player_sprite.position = self.width // 2, self.height // 4
        self.enemy_sprite = arcade.Sprite(":resources:images/animated_characters/zombie/zombie_idle.png", SPRITE_SCALING_ENEMY)
        self.enemy_sprite.position = self.width // 2, self.height // 2

        # Set the background color
        self.background_color = arcade.color.AMAZON

    def on_draw(self) -> None:
        """Render the screen."""
        # Clear the screen. This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites
        self.player_sprite.draw()
        self.enemy_sprite.draw()
        self.bullet_list.draw()
        self.bar_list.draw()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        """Called whenever the mouse moves."""
        self.player_sprite.position = x, y

    def on_update(self, delta_time) -> None:
        """Movement and game logic."""
        # Check if the player is dead. If so, exit the game
        if self.player_sprite.health <= 0:
            arcade.exit()

        # Increase the enemy's timer
        self.enemy_timer += delta_time

        # Update the player's indicator bar position
        self.player_sprite.indicator_bar.position = self.player_sprite.center_x, self.player_sprite.center_y + INDICATOR_BAR_OFFSET

        # Call updates on bullet sprites
        self.bullet_list.update()

        # Check if the enemy can attack. If so, shoot a bullet from the enemy to the player
        if self.enemy_timer >= ENEMY_ATTACK_COOLDOWN:
            self.enemy_timer = 0

            # Create the bullet
            bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING_BULLET)

            # Set the bullet's position
            bullet.position = self.enemy_sprite.position

            # Set the bullet's angle to face the player
            diff_x = self.player_sprite.center_x - self.enemy_sprite.center_x
            diff_y = self.player_sprite.center_y - self.enemy_sprite.center_y
            angle = math.atan2(diff_y, diff_x)
            angle_deg = math.degrees(angle)
            if angle_deg < 0:
                angle_deg += 360
            bullet.angle = angle_deg

            # Give the bullet a velocity towards the player
            bullet.change_x = math.cos(angle) * BULLET_SPEED
            bullet.change_y = math.sin(angle) * BULLET_SPEED

            # Add the bullet to the bullet list
            self.bullet_list.append(bullet)

        # Loop through each bullet
        for bullet in self.bullet_list:
            # Check if the bullet has gone off-screen. If so, kill it
            if bullet.top < 0 or bullet.bottom > SCREEN_HEIGHT or bullet.right < 0 or bullet.left > SCREEN_WIDTH:
                bullet.remove_from_sprite_lists()
                continue

            # Check if the bullet has hit the player
            if arcade.check_for_collision(bullet, self.player_sprite):
                # Damage the player and remove the bullet
                self.player_sprite.health -= BULLET_DAMAGE
                bullet.remove_from_sprite_lists()

                # Set the player's indicator bar fullness
                self.player_sprite.indicator_bar.fullness = self.player_sprite.health / PLAYER_HEALTH


def main() -> None:
    """Main Program."""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
