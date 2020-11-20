from typing import Union

import arcade
from arcade import View, Window
from arcade.gui import UILabel, UIElement
from arcade.gui.layouts.manager import UILayoutManager
from arcade.gui.layouts.utils import valid
from arcade.gui.ui_style import UIStyle

from arcade.gui.layouts import UIAbstractLayout
from arcade.gui.layouts.box import UIBoxLayout


class MyView(View):
    def __init__(self):
        super().__init__()
        self.manager = UILayoutManager()

        self._last_mouse_pos = (0, 0)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)

        style = UIStyle.default_style()
        style.set_class_attrs(
            UILabel.__name__,
        )

        root_layout = self.manager.root_layout

        # top left
        layout_top_left = UIBoxLayout(id='top right')
        layout_top_left.pack(UILabel(text="top=0"))
        layout_top_left.pack(UILabel(text="left=20"))
        layout_top_left.pack(UILabel(text="fill_x=True"), space=20)
        root_layout.pack(layout_top_left, top=0, left=20, fill_x=True)

        # window center
        layout_center = UIBoxLayout(id='center', align='center')
        layout_center.pack(UILabel(text="center_x=0"))
        layout_center.pack(UILabel(text="center_y=0"))
        layout_center.pack(UILabel(text="no fill effect"), space=20)
        root_layout.pack(layout_center, center_x=0, center_y=0)

        # center right
        layout_center_right = UIBoxLayout(vertical=True, align='center', id='right center')
        layout_center_right.pack(UILabel(text="right=0"))
        layout_center_right.pack(UILabel(text="top=0"))
        layout_center_right.pack(UILabel(text="fill_y=True"), space=20)
        root_layout.pack(layout_center_right, right=0, top=0, fill_y=True)

        # center left
        layout_center_left = UIBoxLayout(vertical=True, align='center', id='right center')
        layout_center_left.pack(UILabel(text="left=0"))
        layout_center_left.pack(UILabel(text="center_y=0"))
        layout_center_left.pack(UILabel(text="no fill effect"), space=20)
        root_layout.pack(layout_center_left, left=0, center_y=0)

        # bottom center
        layout_bottom_center = UIBoxLayout(vertical=False, align='center', id='bottom center')
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

        self.draw_borders(self.manager.root_layout)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.S:
            print(self.window.get_location())
        elif symbol == arcade.key.M:
            print(self._last_mouse_pos)
        elif symbol == arcade.key.W:
            print('Window size', self.window.get_size())
        elif symbol == arcade.key.D:
            self.debug_layout(self.manager.root_layout)
        elif symbol == arcade.key.R:
            (self.manager.refresh())

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self._last_mouse_pos = (x, y)


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
