from typing import Union

import arcade
from arcade import View, Window, SpriteSolidColor
from arcade.gui import UILabel, UIElement, UIFlatButton
from arcade.gui.layouts import UIAbstractLayout
from arcade.gui.layouts.box import UIBoxLayout
from arcade.gui.layouts.manager import UILayoutManager
from arcade.gui.layouts.utils import valid
from arcade.gui.ui_style import UIStyle


class MyView(View):
    def __init__(self, window=None):
        super().__init__(window=window)
        self.ui_manager = UILayoutManager(window=window)

        self._drag_start = None
        self._drag_stop = None
        self._last_mouse_pos = (0, 0)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)

        style = UIStyle.default_style()
        style.set_class_attrs(
            UILabel.__name__,
        )

        root_layout = self.ui_manager.root_layout

        ui_flat_button = UIFlatButton(text="no fill effect")

        @ui_flat_button.event('on_click')
        def on_click(*args):
            print('clicked')

        # top left
        layout_top_left = UIBoxLayout(id='top right')
        layout_top_left.pack(UILabel(text="top=0"))
        layout_top_left.pack(UILabel(text="left=20"))
        layout_top_left.pack(UILabel(text="fill_x=True"), space=20)
        root_layout.pack(layout_top_left, top=0, left=20, fill_x=True)

        # window center
        layout_center = UIBoxLayout(
            id='center',
            align='center',
            bg=arcade.color.CARMINE,
            padding=(10, 0, 30, 40),
            border_color=arcade.color.BLACK
        )
        layout_center.pack(UILabel(text="center_x=0"))
        layout_center.pack(UILabel(text="center_y=0"))
        layout_center.pack(UILabel(text="no fill effect"), space=20)
        layout_center.pack(ui_flat_button, space=20)
        root_layout.pack(layout_center, center_x=0, center_y=0)

        # center right
        layout_center_right = UIBoxLayout(vertical=True, align='center', id='right center')
        layout_center_right.pack(UILabel(text="right=0"))
        layout_center_right.pack(UILabel(text="top=0"))
        layout_center_right.pack(UILabel(text="fill_y=True"), space=20)
        root_layout.pack(layout_center_right, right=0, top=0, fill_y=True)

        # center left
        layout_center_left = UIBoxLayout(
            vertical=True,
            align='center',
            id='right center',
            bg=None,
            padding=(10, 0, 30, 40),
            border_color=arcade.color.BLACK
        )
        layout_center_left.pack(UILabel(text="left=0"))
        layout_center_left.pack(UILabel(text="center_y=0"))
        layout_center_left.pack(UILabel(text="no fill effect"), space=20)
        layout_center_left.pack(SpriteSolidColor(width=50, height=50, color=arcade.color.GREEN))
        root_layout.pack(layout_center_left, left=0, center_y=0)

        # bottom center
        layout_bottom_center = UIBoxLayout(vertical=False, align='center', id='bottom center', bg=arcade.color.BEIGE)
        layout_bottom_center.pack(UILabel(text="bottom=0"))
        layout_bottom_center.pack(UILabel(text="center_x=0"), space=10)
        layout_bottom_center.pack(UILabel(text="no fill effect"), space=10)
        root_layout.pack(layout_bottom_center, center_x=0, bottom=60)

        # bottom left
        layout2 = UIBoxLayout(vertical=True, id='bottom left')
        layout2.pack(UILabel(text="bottom=20"))
        layout2.pack(UILabel(text="left=10"))
        layout2.pack(UILabel(text="no fill effect"), space=20)
        root_layout.pack(layout2, left=10, bottom=20)

        self.ui_manager.refresh()

        self.debug_layout(root_layout)

        print(
            layout2.left,
            layout2.top,
            layout2.right,
            layout2.bottom,
            valid(layout2)
        )

    def debug_layout(self, element: Union[UIElement, UIAbstractLayout], prefix=''):
        print(
            f'{prefix}{type(element).__name__}[{getattr(element, "id", "")}]: '
            f'ltrb/wh: {element.left}, {element.top}, {element.right},{element.bottom}/ {element.width}, {element.height}'
            f' {valid(element) if isinstance(element, UIAbstractLayout) else ""}')

        if isinstance(element, UIAbstractLayout):
            for e in element:
                self.debug_layout(e, '\t' + prefix)

    def draw_borders(self, element: Union[UIElement, UIAbstractLayout]):
        l, r, t, b = element.left, element.right, element.top, element.bottom
        arcade.draw_lrtb_rectangle_outline(l, r, t, b, arcade.color.RED)

        if isinstance(element, UIAbstractLayout):
            for e in element:
                self.draw_borders(e)

    def on_draw(self):
        arcade.start_render()

        self.ui_manager.on_draw()

        self.draw_borders(self.ui_manager.root_layout)
        if self._drag_start and self._drag_stop:
            arcade.draw_line(*self._drag_start, *self._drag_stop, arcade.color.RED, line_width=2)

            distance = abs(self._drag_start[0] - self._drag_stop[0]), abs(self._drag_start[1] - self._drag_stop[1])
            text_pos = (self._drag_start[0] + self._drag_stop[0])//2, (self._drag_start[1] + self._drag_stop[1])//2
            arcade.draw_text(f'x:{distance[0]}, y:{distance[1]}', *text_pos, arcade.color.BLACK, font_size=20, bold=True)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.S:
            print(self.window.get_location())
        elif symbol == arcade.key.M:
            print(self._last_mouse_pos)
        elif symbol == arcade.key.W:
            print('Window size', self.window.get_size())
        elif symbol == arcade.key.D:
            self.debug_layout(self.ui_manager.root_layout)
        elif symbol == arcade.key.R:
            (self.ui_manager.refresh())

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self._last_mouse_pos = (x, y)
        self._drag_stop = x, y

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self._drag_start = x, y

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        self._drag_start = None


def main():
    window = Window(resizable=True)

    # TODO remove me
    if len(arcade.get_screens()) > 1:
        window.set_location(2012, 256)

    view = MyView()
    window.show_view(view)

    arcade.run()


if __name__ == '__main__':
    main()
