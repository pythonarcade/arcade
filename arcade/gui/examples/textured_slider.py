"""
Create a slider using a custom texture subclass

The initial theme is a 90s sci-fi style, but you can replace the textures
in this example to match the theme of your project.

If arcade and Python are properly installed, you can run this example with:
python -m arcade.gui.examples.textured_slider
"""
from typing import Union

import arcade
from arcade import Texture
from arcade.gui import UIManager, Surface, UIAnchorLayout, NinePatchTexture
from arcade.gui.widgets.slider import UISlider


class UITextureSlider(UISlider):
    """
    A custom slider subclass which supports textures.

    You can copy this as-is into your own project, or you can modify
    the class to have more features as needed.
    """

    def __init__(
        self,
        bar: Union[Texture, NinePatchTexture],
        thumb: Union[Texture, NinePatchTexture],
        style=None,
        **kwargs
    ):
        self.bar = bar
        self.thumb = thumb
        style = style or UISlider.DEFAULT_STYLE

        super().__init__(style=style, **kwargs)

    def do_render(self, surface: Surface):
        style: UISlider.UIStyle = self.get_current_style()  # type: ignore

        self.prepare_render(surface)

        surface.draw_texture(0, 0, self.width, self.height, self.bar)

        # TODO accept constructor params
        slider_height = self.height // 4
        slider_left_x = self._x_for_value(self.vmin)
        cursor_center_x = self.value_x

        slider_bottom = (self.height - slider_height) // 2

        # slider
        arcade.draw_xywh_rectangle_filled(
            slider_left_x - self.x,
            slider_bottom,
            cursor_center_x - slider_left_x,
            slider_height,
            style.filled_bar,
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


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui = UIManager()

        bar_tex = arcade.load_texture(":resources:gui_basic_assets/slider_bar.png")
        thumb_tex = arcade.load_texture(":resources:gui_basic_assets/slider_thumb.png")
        self.slider = UITextureSlider(bar_tex, thumb_tex)

        # Add button to UIManager, use UIAnchorWidget defaults to center on screen
        self.ui.add(UIAnchorLayout(children=[self.slider]))

    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_BLUE_GRAY
        # Enable UIManager when view is shown to catch window events
        self.ui.enable()

    def on_hide_view(self):
        self.ui.disable()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.slider.disabled = not self.slider.disabled

    def on_draw(self):
        self.clear()
        self.ui.draw()


if __name__ == '__main__':
    window = arcade.Window(800, 600, "UIExample", resizable=True)
    window.show_view(MyView())
    window.run()
