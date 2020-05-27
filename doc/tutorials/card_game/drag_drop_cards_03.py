"""
Drag and drop cards

python -m arcade.examples.drag_drop_cards
"""
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Drag and Drop Cards"
CARD_VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
# CARD_VALUES = ["A", "2"]

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

        self.card_list: arcade.SpriteList = arcade.SpriteList()
        self.pile_list: arcade.SpriteList = arcade.SpriteList()
        self.held_card = None
        self.held_card_original_position = None

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        for i, card_value in enumerate(CARD_VALUES):
            card = arcade.Sprite(f":resources:images/cards/cardClubs{card_value}.png")
            card.position = 100 + i * 40, 110
            self.card_list.append(card)

        for i, card_value in enumerate(CARD_VALUES):
            card = arcade.Sprite(f":resources:images/cards/cardHearts{card_value}.png")
            card.position = 100 + i * 40, 310
            self.card_list.append(card)

        pile = arcade.SpriteSolidColor(170, 220, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = 100, 530
        self.pile_list.append(pile)

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        self.pile_list.draw()
        self.card_list.draw()

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """
        cards = arcade.get_sprites_at_point((x, y), self.card_list)

        if len(cards) > 0:
            self.held_card = cards[-1]
            self.held_card_original_position = self.held_card.position
            index = self.card_list.index(self.held_card)

            for i in range(index, len(self.card_list) - 1):
                self.card_list[i] = self.card_list[i + 1]
            self.card_list[len(self.card_list) - 1] = self.held_card

        self.card_list._calculate_sprite_buffer()

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """ Called when the user presses a mouse button. """
        pile, distance = arcade.get_closest_sprite(self.held_card, self.pile_list)
        if arcade.check_for_collision(self.held_card, pile):
            self.held_card.position = pile.position
        else:
            self.held_card.position = self.held_card_original_position
        self.held_card = None
        self.card_list._calculate_sprite_buffer()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        if self.held_card:
            self.held_card.center_x += dx
            self.held_card.center_y += dy


def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
