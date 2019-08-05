"""
This program shows how to:
  * Shows how to get two, independent WindowWithViews open at the same time.
  * Demonstrate how multiple WindowWithViews can change their current View
    independent of the other WindowWithViews.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.different_views_multiple_windows
"""
import arcade

WIDTH = 400
HEIGHT = 300


class GreenView(arcade.View):
    def on_draw(self):
        arcade.start_render()
        arcade.draw_xywh_rectangle_filled(100, 100, 50, 50, arcade.color.GREEN)

    def on_mouse_press(self, x, y, button, modifiers):
        self.parent.show_view(PurpleView())
        self.parent.click_count += 1
        print('click count', self.parent.click_count, id(self.parent))


class PurpleView(arcade.View):
    def on_draw(self):
        arcade.start_render()
        arcade.draw_xywh_rectangle_filled(100, 100, 50, 50, arcade.color.PURPLE)

    def on_mouse_press(self, x, y, button, modifiers):
        self.parent.show_view(RedView())
        self.parent.click_count += 1
        print('click count', self.parent.click_count, id(self.parent))


class RedView(arcade.View):
    def on_draw(self):
        arcade.start_render()
        arcade.draw_xywh_rectangle_filled(100, 100, 50, 50, arcade.color.RED)

    def on_mouse_press(self, x, y, button, modifiers):
        self.parent.show_view(GreenView())
        self.parent.click_count += 1
        print('click count', self.parent.click_count, id(self.parent))


win1 = arcade.Window(WIDTH, HEIGHT, 'Win 1')
win1.set_location(50, 100)
win1.click_count = 0
win1.show_view(GreenView())

win2 = arcade.Window(WIDTH, HEIGHT, 'Win 2')
win2.set_location(WIDTH + 100, 100)
win2.click_count = 0
win2.show_view(GreenView())

arcade.run()
