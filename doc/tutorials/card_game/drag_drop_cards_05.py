"""
Drag and drop cards

python -m arcade.examples.drag_drop_cards
"""
import random
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Drag and Drop Cards"
CARD_VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
CARD_SUITS = ["Clubs", "Hearts", "Spades", "Diamonds"]

PILE_COUNT = 5
PULL_PILE = 0
TOP_PILE_1 = 1
TOP_PILE_2 = 2
TOP_PILE_3 = 3
TOP_PILE_4 = 4


class Card(arcade.Sprite):
    def __init__(self, suit, value, scale=1):
        self.card_value = value
        self.card_suit = suit
        card_name = f":resources:images/cards/card{self.card_suit}{self.card_value}.png"
        super().__init__(card_name, scale, calculate_hit_box=False)


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

        self.card_list: arcade.SpriteList = arcade.SpriteList()
        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()
        self.held_card = None
        self.held_card_original_position = None

        self.piles = [[] for i in range(PILE_COUNT)]

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        for j, card_suit in enumerate(CARD_SUITS):
            for i, card_value in enumerate(CARD_VALUES):
                card = Card(card_suit, card_value, 0.5)
                card.position = 100, 110
                self.card_list.append(card)

        # Shuffle
        for pos1 in range(len(self.card_list)):
            pos2 = random.randrange(len(self.card_list))
            self.card_list[pos1], self.card_list[pos2] = self.card_list[pos2], self.card_list[pos1]

        for card in self.card_list:
            self.piles[PULL_PILE].append(card)

        pile = arcade.SpriteSolidColor(85, 110, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = 100, 110
        self.pile_mat_list.append(pile)

        pile = arcade.SpriteSolidColor(85, 110, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = 70, 630
        self.pile_mat_list.append(pile)

        pile = arcade.SpriteSolidColor(85, 110, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = 170, 630
        self.pile_mat_list.append(pile)

        pile = arcade.SpriteSolidColor(85, 110, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = 270, 630
        self.pile_mat_list.append(pile)

        pile = arcade.SpriteSolidColor(85, 110, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = 370, 630
        self.pile_mat_list.append(pile)


    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        self.pile_mat_list.draw()
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

    def remove_card_from_pile(self, card):

        for pile in self.piles:
            if card in pile:
                pile.remove(card)
                break

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """ Called when the user presses a mouse button. """
        if self.held_card is None:
            return

        pile, distance = arcade.get_closest_sprite(self.held_card, self.pile_mat_list)
        if arcade.check_for_collision(self.held_card, pile):
            self.held_card.position = pile.position
            self.remove_card_from_pile(self.held_card)
            index = self.pile_mat_list.index(pile)
            self.piles[index].append(self.held_card)
        else:
            self.held_card.position = self.held_card_original_position
        self.held_card = None
        self.card_list._calculate_sprite_buffer()

        print()
        print(f"Pull deck: {len(self.piles[PULL_PILE])}")
        print(f"Pull deck: {len(self.piles[TOP_PILE_1])}")
        print(f"Pull deck: {len(self.piles[TOP_PILE_2])}")
        print(f"Pull deck: {len(self.piles[TOP_PILE_3])}")
        print(f"Pull deck: {len(self.piles[TOP_PILE_4])}")

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
