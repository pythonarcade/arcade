import arcade
from arcade.gui.widgets.slider import UISlider
from arcade.gui import UIManager, UILabel
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

        ui_anchor_layout = arcade.gui.widgets.layout.UIAnchorLayout()
        ui_anchor_layout.add(child=ui_slider, anchor_x="center_x", anchor_y="center_y")
        ui_anchor_layout.add(child=label, align_y=50)
        self.manager.add(ui_anchor_layout)

    def on_draw(self):
        self.clear()
        self.manager.draw()


if __name__ == "__main__":
    window = UIMockup()
    arcade.run()
