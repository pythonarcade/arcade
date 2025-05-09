"""
Section Example 3:

This shows how sections work with a very small example

What's key here is to understand how sections can isolate code that otherwise
 goes packed together in the view.
Also, note that events are received on each section only based on the
 section configuration. This way you don't have to check every time if the mouse
 position is on top of some area.

Note:
 - Event dispatching (two sections will receive on_key_press and on_key_release)
 - Prevent dispatching to allow some events to stop propagating
 - Event draw, update and event delivering order based on section_manager
   sections list order
 - Section "enable" property to show or hide sections
 - Modal Sections: sections that draw last but capture all events and also stop
   other sections from updating.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sections_demo_3
"""

from math import sqrt

import arcade
from arcade import Section, SectionManager
from arcade.types import Color

INFO_BAR_HEIGHT = 40
PANEL_WIDTH = 200
SPRITE_SPEED = 1

COLOR_LIGHT = Color.from_hex_string("#D9BBA0")
COLOR_DARK = Color.from_hex_string("#0D0D0D")
COLOR_1 = Color.from_hex_string("#2A1459")
COLOR_2 = Color.from_hex_string("#4B89BF")
COLOR_3 = Color.from_hex_string("#03A688")


class Ball(arcade.SpriteCircle):
    """The moving ball"""

    def __init__(self, radius, color):
        super().__init__(radius, color)

        self.bounce_count: int = 0  # to count the number of bounces

    @property
    def speed(self):
        # return euclidian distance * current fps (60 default)
        return int(sqrt(pow(self.change_x, 2) + pow(self.change_y, 2)) * 60)


class ModalSection(Section):
    """A modal section that represents a popup that waits for user input"""

    def __init__(self, left: int, bottom: int, width: int, height: int):
        super().__init__(left, bottom, width, height, modal=True, enabled=False)

        # modal button
        self.button = arcade.SpriteSolidColor(100, 50, color=arcade.color.RED)
        pos = self.left + self.width / 2, self.bottom + self.height / 2
        self.button.position = pos

    def on_draw(self):
        # draw modal frame and button
        arcade.draw_lrbt_rectangle_filled(
            self.left, self.right, self.bottom, self.top, arcade.color.GRAY
        )
        arcade.draw_lrbt_rectangle_outline(
            self.left, self.right, self.bottom, self.top, arcade.color.WHITE
        )
        self.draw_button()

    def draw_button(self):
        # draws the button and button text
        arcade.draw_sprite(self.button)
        arcade.draw_text(
            "Close Modal",
            self.button.left + 5,
            self.button.bottom + self.button.height / 2,
            arcade.color.WHITE,
        )

    def on_resize(self, width: int, height: int):
        """set position on screen resize"""
        self.left = width // 3
        self.bottom = (height // 2) - self.height // 2
        pos = self.left + self.width / 2, self.bottom + self.height / 2
        self.button.position = pos

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """Check if the button is pressed"""
        if self.button.collides_with_point((x, y)):
            self.enabled = False


class InfoBar(Section):
    """This is the top bar of the screen where info is showed"""

    @property
    def ball(self):
        return self.view.map.ball

    def on_draw(self):
        # draw game info
        arcade.draw_lrbt_rectangle_filled(self.left, self.right, self.bottom, self.top, COLOR_DARK)
        arcade.draw_lrbt_rectangle_outline(
            self.left, self.right, self.bottom, self.top, COLOR_LIGHT
        )
        arcade.draw_text(
            f"Ball bounce count: {self.ball.bounce_count}",
            self.left + 20,
            self.top - self.height / 1.6,
            COLOR_LIGHT,
        )

        ball_change_axis = self.ball.change_x, self.ball.change_y
        arcade.draw_text(
            f"Ball change in axis: {ball_change_axis}",
            self.left + 220,
            self.top - self.height / 1.6,
            COLOR_LIGHT,
        )
        arcade.draw_text(
            f"Ball speed: {self.ball.speed} pixels/second",
            self.left + 480,
            self.top - self.height / 1.6,
            COLOR_LIGHT,
        )

    def on_resize(self, width: int, height: int):
        # stick to the top
        self.width = width
        self.bottom = height - self.view.info_bar.height


class Panel(Section):
    """This is the Panel to the right where buttons and info is showed"""

    def __init__(self, left: int, bottom: int, width: int, height: int, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

        # create buttons
        self.button_stop = self.new_button(arcade.color.ARSENIC)
        self.button_toggle_info_bar = self.new_button(COLOR_1)

        self.button_show_modal = self.new_button(COLOR_2)
        # to show the key that's actually pressed
        self.pressed_key: int | None = None

    @staticmethod
    def new_button(color):
        # helper to create new buttons
        return arcade.SpriteSolidColor(100, 50, color=color)

    def draw_button_stop(self):
        arcade.draw_text(
            "Press button to stop the ball", self.left + 10, self.top - 40, COLOR_LIGHT, 10
        )
        arcade.draw_sprite(self.button_stop)

    def draw_button_toggle_info_bar(self):
        arcade.draw_text(
            "Press to toggle info_bar", self.left + 10, self.top - 140, COLOR_LIGHT, 10
        )
        arcade.draw_sprite(self.button_toggle_info_bar)

    def draw_button_show_modal(self):
        arcade.draw_sprite(self.button_show_modal)
        arcade.draw_text(
            "Show Modal", self.left - 37 + self.width / 2, self.bottom + 95, COLOR_DARK, 10
        )

    def on_draw(self):
        arcade.draw_lrbt_rectangle_filled(self.left, self.right, self.bottom, self.top, COLOR_DARK)
        arcade.draw_lrbt_rectangle_outline(
            self.left, self.right, self.bottom, self.top, COLOR_LIGHT
        )
        self.draw_button_stop()
        self.draw_button_toggle_info_bar()

        if self.pressed_key:
            arcade.draw_text(
                f"Pressed key code: {self.pressed_key}",
                self.left + 10,
                self.top - 240,
                COLOR_LIGHT,
                9,
            )

        self.draw_button_show_modal()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.button_stop.collides_with_point((x, y)):
            self.view.map.ball.stop()
        elif self.button_toggle_info_bar.collides_with_point((x, y)):
            self.view.info_bar.enabled = not self.view.info_bar.enabled
        elif self.button_show_modal.collides_with_point((x, y)):
            self.view.modal_section.enabled = True

    def on_resize(self, width: int, height: int):
        # stick to the right
        self.left = width - self.width
        self.height = height - self.view.info_bar.height
        self.button_stop.position = self.left + self.width / 2, self.top - 80

        pos = self.left + self.width / 2, self.top - 180
        self.button_toggle_info_bar.position = pos

        pos = self.left + self.width / 2, self.bottom + 100
        self.button_show_modal.position = pos

    def on_key_press(self, symbol: int, modifiers: int):
        self.pressed_key = symbol

    def on_key_release(self, _symbol: int, _modifiers: int):
        self.pressed_key = None


class Map(Section):
    """This represents the place where the game takes place"""

    def __init__(self, left: int, bottom: int, width: int, height: int, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

        self.ball = Ball(20, COLOR_3)
        self.ball.position = 60, 60
        self.sprite_list: arcade.SpriteList = arcade.SpriteList()
        self.sprite_list.append(self.ball)

        self.pressed_key: int | None = None

    def on_update(self, delta_time: float):
        if self.pressed_key:
            if self.pressed_key == arcade.key.UP:
                self.ball.change_y += SPRITE_SPEED
            elif self.pressed_key == arcade.key.RIGHT:
                self.ball.change_x += SPRITE_SPEED
            elif self.pressed_key == arcade.key.DOWN:
                self.ball.change_y -= SPRITE_SPEED
            elif self.pressed_key == arcade.key.LEFT:
                self.ball.change_x -= SPRITE_SPEED

        self.sprite_list.update()

        if self.ball.top >= self.top or self.ball.bottom <= self.bottom:
            self.ball.change_y *= -1
            self.ball.bounce_count += 1
        if self.ball.left <= self.left or self.ball.right >= self.right:
            self.ball.change_x *= -1
            self.ball.bounce_count += 1

    def on_draw(self):
        arcade.draw_lrbt_rectangle_filled(self.left, self.right, self.bottom, self.top, COLOR_DARK)
        arcade.draw_lrbt_rectangle_outline(
            self.left, self.right, self.bottom, self.top, COLOR_LIGHT
        )
        self.sprite_list.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        self.pressed_key = symbol

    def on_key_release(self, _symbol: int, _modifiers: int):
        self.pressed_key = None

    def on_resize(self, width: int, height: int):
        self.width = width - self.view.panel.width
        self.height = height - self.view.info_bar.height


class GameView(arcade.View):
    """The game itself"""

    def __init__(self):
        super().__init__()

        # create and store the modal, so we can set
        # self.modal_section.enabled = True to show it
        self.modal_section = ModalSection(
            (self.window.width / 2) - 150,
            (self.window.height / 2) - 100,
            300,
            200,
        )

        # we set accept_keyboard_events to False (default to True)
        self.info_bar = InfoBar(
            0,
            self.window.height - INFO_BAR_HEIGHT,
            self.window.width,
            INFO_BAR_HEIGHT,
            accept_keyboard_keys=False,
        )

        # as prevent_dispatch is on by default, we let pass the events to the
        # following Section: the map
        self.panel = Panel(
            self.window.width - PANEL_WIDTH,
            0,
            PANEL_WIDTH,
            self.window.height - INFO_BAR_HEIGHT,
            prevent_dispatch={False},
        )
        self.map = Map(0, 0, self.window.width - PANEL_WIDTH, self.window.height - INFO_BAR_HEIGHT)

        # add the sections
        self.section_manager = SectionManager(self)
        self.section_manager.add_section(self.modal_section)
        self.section_manager.add_section(self.info_bar)
        self.section_manager.add_section(self.panel)
        self.section_manager.add_section(self.map)

    def on_show_view(self) -> None:
        self.section_manager.enable()

    def on_hide_view(self) -> None:
        self.section_manager.disable()

    def on_draw(self):
        self.clear()


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(resizable=True)

    # Create the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
