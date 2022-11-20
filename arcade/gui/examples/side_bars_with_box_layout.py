import arcade
from arcade.gui import UIManager, UIDummy, UIBoxLayout


class DemoWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        self.manager = UIManager()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        v_box = UIBoxLayout(size_hint=(1, 1))

        top_bar = UIDummy(height=50, size_hint=(1, 0), size_hint_min=(None, 50))
        v_box.add(top_bar)

        h_box = UIBoxLayout(size_hint=(1, 1), vertical=False)
        left_bar = UIDummy(width=50, size_hint=(0, 1), size_hint_min=(50, None))
        h_box.add(left_bar)
        center_area = UIDummy(size_hint=(1, 1))
        h_box.add(center_area)
        right_bar = UIDummy(size_hint=(0, 1), size_hint_min=(100, None))
        h_box.add(right_bar)
        v_box.add(h_box)

        bottom_bar = UIDummy(height=100, size_hint=(1, 0), size_hint_min=(None, 100))
        v_box.add(bottom_bar)

        self.manager.add(v_box)

    def on_show(self):
        self.manager.enable()

    def on_hide(self):
        self.manager.disable()

    def on_key_press(self, symbol: int, modifiers: int):
        pass

    def on_draw(self):
        arcade.start_render()
        self.manager.draw()


if __name__ == "__main__":
    DemoWindow().run()
