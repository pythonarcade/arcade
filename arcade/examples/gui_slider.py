import arcade
from arcade.experimental.uislider import UISlider
from arcade.gui import UIManager, UIAnchorWidget, UILabel
from arcade.gui.events import UIOnChangeEvent


class UIMockup(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        self.manager = UIManager()
        self.manager.enable()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        ui_slider = UISlider(value=50, width=300, height=50)
        label = UILabel(text=f"{ui_slider.value:02.0f}")

        @ui_slider.event()
        def on_change(event: UIOnChangeEvent):
            label.text = f"{ui_slider.value:02.0f}"
            label.fit_content()

        self.manager.add(UIAnchorWidget(child=ui_slider))
        self.manager.add(UIAnchorWidget(child=label, align_y=100))

    def on_draw(self):
        self.clear()
        self.manager.draw()


if __name__ == '__main__':
    window = UIMockup()
    arcade.run()
