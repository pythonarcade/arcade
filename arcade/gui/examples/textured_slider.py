import arcade
from arcade import Window, View, Texture
from arcade.experimental.uistyle import UISliderStyle
from arcade.gui import UIManager, Surface, UIAnchorLayout
from arcade.gui.widgets.slider import UISlider


class UITextureSlider(UISlider):
    """
    Slider using
    """

    def __init__(self, bar: Texture, thumb: Texture, **kwargs):
        self.bar = bar
        self.thumb = thumb
        style = UISliderStyle(
            normal_filled_bar=(180, 180, 140),
            hovered_filled_bar=(200, 200, 165),
            pressed_filled_bar=(225, 225, 180),
        )

        super().__init__(style=style, **kwargs)

    def do_render(self, surface: Surface):
        state = "pressed" if self.pressed else "hovered" if self.hovered else "normal"

        self.prepare_render(surface)

        surface.draw_texture(0, 0, self.width, self.height, self.bar)

        # TODO accept constructor params
        slider_height = self.height // 4
        slider_left_x = self._x_for_value(self.vmin)
        cursor_center_x = self.value_x

        slider_bottom = (self.height - slider_height) // 2

        # slider
        fg_slider_color = self.style[f"{state}_filled_bar"]
        arcade.draw_xywh_rectangle_filled(
            slider_left_x - self.x,
            slider_bottom,
            cursor_center_x - slider_left_x,
            slider_height,
            fg_slider_color,
        )

        # cursor
        rel_cursor_x = cursor_center_x - self.x
        surface.draw_texture(
            x=rel_cursor_x - self.thumb.width // 4 + 2,
            y=0,
            width=self.thumb.width // 2,
            height=self.height,
            tex=self.thumb,
        )


class MyView(View):
    def __init__(self):
        super().__init__()

        self.manager = UIManager()

        bar_tex = arcade.load_texture(":resources:gui_basic_assets/slider_bar.png")
        thumb_tex = arcade.load_texture(":resources:gui_basic_assets/slider_bar.png")
        self.slider = UITextureSlider(bar_tex, thumb_tex)

        # Add button to UIManager, use UIAnchorWidget defaults to center on screen
        self.manager.add(UIAnchorLayout(children=[self.slider]))

    def on_show_view(self):
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()


if __name__ == "__main__":
    window = Window()
    view = MyView()
    window.show_view(view)
    arcade.run()
    # pass
