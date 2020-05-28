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

PILE_COUNT = 13
PULL_PILE_UP = 0
PULL_PILE_DOWN = 1
TOP_PILE_1 = 2
TOP_PILE_2 = 3
TOP_PILE_3 = 4
TOP_PILE_4 = 5
PLAY_PILE_1 =6
PLAY_PILE_2 = 7
PLAY_PILE_3 = 8
PLAY_PILE_4 = 9
PLAY_PILE_5 = 10
PLAY_PILE_6 = 11
PLAY_PILE_7 = 12


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
        self.held_cards = []
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
            self.piles[PULL_PILE_UP].append(card)

        pile = arcade.SpriteSolidColor(85, 110, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = 100, 110
        self.pile_mat_list.append(pile)

        pile = arcade.SpriteSolidColor(85, 110, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = 200, 110
        self.pile_mat_list.append(pile)

        for i in range(4):
            pile = arcade.SpriteSolidColor(85, 110, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = 70 + i * 100, 630
            self.pile_mat_list.append(pile)

        for i in range(7):
            pile = arcade.SpriteSolidColor(85, 110, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = 70 + i * 100, 430
            self.pile_mat_list.append(pile)

        for i in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
            for j in range(i - PLAY_PILE_1 + 1):
                card = self.piles[PULL_PILE_UP].pop()
                self.piles[i].append(card)
                self.pull_to_top(card)
                card.position = self.pile_mat_list[i].position


    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        self.pile_mat_list.draw()
        self.card_list.draw()

    def pull_to_top(self, card):
        index = self.card_list.index(card)
        for i in range(index, len(self.card_list) - 1):
            self.card_list[i] = self.card_list[i + 1]
        self.card_list[len(self.card_list) - 1] = card

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """
        cards = arcade.get_sprites_at_point((x, y), self.card_list)

        if len(cards) > 0:
            primary_card = cards[-1]
            self.held_cards = [primary_card]
            self.held_cards_original_position = [self.held_cards[0].position]
            self.pull_to_top(self.held_cards[0])

            pile_index = self.get_pile_for_card(primary_card)
            card_index = self.piles[pile_index].index(primary_card)
            for i in range(card_index + 1, len(self.piles[pile_index])):
                card = self.piles[pile_index][i]
                self.held_cards.append(card)
                self.held_cards_original_position.append(card.position)
                self.pull_to_top(card)

    def remove_card_from_pile(self, card):
        for pile in self.piles:
            if card in pile:
                pile.remove(card)
                break

    def get_pile_for_card(self, card):
        for index, pile in enumerate(self.piles):
            if card in pile:
                return index

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """ Called when the user presses a mouse button. """
        if len(self.held_cards) == 0:
            return

        pile, distance = arcade.get_closest_sprite(self.held_cards[0], self.pile_mat_list)
        reset = True
        if arcade.check_for_collision(self.held_cards[0], pile):
            index = self.pile_mat_list.index(pile)
            if not index == self.get_pile_for_card(self.held_cards[0]):

                if index >= PLAY_PILE_1 and index <= PLAY_PILE_7:
                    if len(self.piles[index]) > 0:
                        top_card = self.piles[index][-1]
                        for i, dropped_card in enumerate(self.held_cards):
                            dropped_card.position = top_card.center_x, top_card.center_y - 20 * (i + 1)
                    else:
                        for dropped_card in self.held_cards:
                            dropped_card.position = pile.center_x, pile.center_y
                else:
                    self.held_cards[0].position = pile.position
                for card in self.held_cards:
                    self.remove_card_from_pile(card)
                    self.piles[index].append(card)
                reset = False

        if reset:
            for index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[index]

        self.held_cards = []

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy


def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
