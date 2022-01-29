"""
This shows how sections work with a very small example

What's key here is to understand how sections can isolate code that otherwise
 goes packed together in the view.
Also, note that events are received on each section only based on the
 section configuration. This way you don't have to check every time if the mouse
 position is on top of some area.

"""
import arcade
from arcade.sections import Section

INFO_BAR_HEIGHT = 40
PANEL_WIDTH = 200
SPRITE_SPEED = 1


class Ball(arcade.SpriteCircle):

    def __init__(self, radius, color):
        super().__init__(radius, color)

        self.bounce_count = 0

    @property
    def speed(self):
        return round((abs(self.change_x) + abs(self.change_y)) * 60, 2)


class InfoBar(Section):

    @property
    def ball(self):
        return self.view.map.ball

    def on_draw(self):
        arcade.draw_lrtb_rectangle_filled(self.left, self.right, self.top,
                                          self.bottom, arcade.color.GRAY)
        arcade.draw_lrtb_rectangle_outline(self.left, self.right, self.top,
                                           self.bottom, arcade.color.WHITE)
        arcade.draw_text(f'Ball bounce count: {self.ball.bounce_count}', self.left + 20,
                         self.top - self.height / 1.6, arcade.color.BLUE)

        arcade.draw_text(f'Ball change in axis: {(self.ball.change_x, self.ball.change_y)}',
                         self.left + 220, self.top - self.height / 1.6, arcade.color.BLUE)
        arcade.draw_text(f'Ball speed: {self.ball.speed} pixels/second',
                         self.left + 480, self.top - self.height / 1.6, arcade.color.BLUE)

    def on_resize(self, width: int, height: int):
        # stick to the top
        self.width = width
        self.bottom = height - self.view.info_bar.height


class Panel(Section):

    def __init__(self, left: float, bottom: float, width: float, height: float, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

        self.button_stop = self.new_button(arcade.color.PUMPKIN)
        self.button_toogle_info_bar = self.new_button(arcade.color.YELLOW)

    @staticmethod
    def new_button(color):
        return arcade.SpriteSolidColor(100, 50, color)

    def draw_button_stop(self):
        arcade.draw_text('Press button to stop the ball', self.left + 10, self.top - 40, arcade.color.BLACK, 9)
        self.button_stop.draw()

    def draw_button_toogle_info_bar(self):
        arcade.draw_text('Press to toogle info_bar', self.left + 10, self.top - 140, arcade.color.BLACK, 9)
        self.button_toogle_info_bar.draw()

    def on_draw(self):
        arcade.draw_lrtb_rectangle_filled(self.left, self.right, self.top,
                                          self.bottom, arcade.color.BROWN)
        arcade.draw_lrtb_rectangle_outline(self.left, self.right, self.top,
                                           self.bottom, arcade.color.WHITE)
        self.draw_button_stop()
        self.draw_button_toogle_info_bar()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.button_stop.collides_with_point((x, y)):
            self.view.map.ball.stop()
        elif self.button_toogle_info_bar.collides_with_point((x, y)):
            self.view.info_bar.enabled = not self.view.info_bar.enabled

    def on_resize(self, width: int, height: int):
        # stick to the right
        self.left = width - self.width
        self.height = height - self.view.info_bar.height
        self.button_stop.position = self.left + self.width / 2, self.top - 80
        self.button_toogle_info_bar.position = self.left + self.width / 2, self.top - 180


class Map(Section):

    def __init__(self, left: float, bottom: float, width: float, height: float, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

        self.ball = Ball(20, arcade.color.RED)
        self.ball.position = 60, 60
        self.sprite_list = arcade.SpriteList()
        self.sprite_list.append(self.ball)

        self.pressed_key = None

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
        arcade.draw_lrtb_rectangle_outline(self.left, self.right, self.top,
                                           self.bottom, arcade.color.WHITE)
        self.sprite_list.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        self.pressed_key = symbol

    def on_key_release(self, _symbol: int, _modifiers: int):
        self.pressed_key = None

    def on_resize(self, width: int, height: int):
        self.width = width - self.view.panel.width
        self.height = height - self.view.info_bar.height


class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        self.info_bar = InfoBar(0, self.window.height - INFO_BAR_HEIGHT, self.window.width, INFO_BAR_HEIGHT)
        self.panel = Panel(self.window.width - PANEL_WIDTH, 0, PANEL_WIDTH, self.window.height - INFO_BAR_HEIGHT)
        self.map = Map(0, 0, self.window.width - PANEL_WIDTH, self.window.height - INFO_BAR_HEIGHT,
                       accept_keyboard_events=True)

        self.section_manager.add_section(self.info_bar)
        self.section_manager.add_section(self.panel)
        self.section_manager.add_section(self.map)

    def on_draw(self):
        arcade.start_render()


def main():
    window = arcade.Window(resizable=True)
    game = GameView()

    window.show_view(game)

    arcade.run()


if __name__ == '__main__':
    main()
