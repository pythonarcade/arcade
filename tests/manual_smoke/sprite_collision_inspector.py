from __future__ import annotations

import builtins
from typing import TypeVar, Type, Generic, Any, Callable

from pyglet.math import Vec2

import arcade
from arcade import SpriteList, Sprite, SpriteSolidColor, load_texture
from arcade.gui import UIManager, NinePatchTexture, UIInputText, UIWidget, UIBoxLayout
from arcade.types import RGBOrA255, Color

GRID_REGULAR = arcade.color.GREEN.replace(a=128)
GRID_HIGHLIGHT = arcade.color.GREEN


TEX_GREY_PANEL_RAW = load_texture(":resources:gui_basic_assets/window/grey_panel.png")

T = TypeVar('T')

def _tname(t: Any) -> str:
    if not isinstance(t, builtins.type):
        return  t.__class__.__name__
    else:
        return t.__name__


class TypedTextInput(UIInputText, Generic[T]):
    def __init__(
        self,
        parsed_type: Type[T],
        *,
        to_str: Callable[[T], str] = repr,
        from_str: Callable[[str], T] | None = None,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 24,
        text: str = "",
        font_name=("Arial",),
        font_size: float = 12,
        text_color: RGBOrA255 = (0, 0, 0, 255),
        error_color: RGBOrA255 = arcade.color.RED,
        multiline=False,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        **kwargs,
    ):
        if not isinstance(type, builtins.type):
            raise TypeError(f"Expected a type, but got {type}")
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            text=text,
            font_name=font_name,
            font_size=font_size,
            text_color=text_color,
            multiline=multiline,
            caret_color=text_color,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            **kwargs
        )
        self._error_color = error_color
        self._parsed_type: Type[T] = parsed_type
        self._to_str = to_str
        self._from_str = from_str or parsed_type
        self._parsed_value: T = self._from_str(self.text)

    @property
    def value(self) -> T:
        return self._parsed_value

    @value.setter
    def value(self, new_value: T) -> None:
        if not isinstance(new_value, self._parsed_type):
            raise TypeError(
                f"This {_tname(self)} is of inner type {_tname(self._parsed_type)}"
                f", but got {new_value!r}, a {_tname(new_value)}"
            )
        try:
            self._parsed_value = self._from_str(new_value)
            self.doc.text = self._to_str(new_value)
            self.color = self._text_color
        except Exception as e:
            self.color = self._error_color
            raise e

        self.trigger_full_render()

    @property
    def color(self) -> Color:
        return self._color

    @color.setter
    def color(self, new_color: RGBOrA255) -> None:
        # lol, efficiency
        validated = Color.from_iterable(new_color)
        if self._color == validated:
            return

        self.caret.color = validated
        self.doc.set_style(
            0, len(self.text), dict(color=validated)
        )
        self.trigger_full_render()

    @property
    def text(self) -> str:
        return self.doc.text

    @text.setter
    def text(self, new_text: str) -> None:
        try:
            self.doc.text = new_text
            validated: T = self._from_str(new_text)
            self._parsed_value = validated
            self.color = self._text_color
        except Exception as e:
            self.color = self._error_color
            raise e



def draw_crosshair(
    where: tuple[float, float],
    color=arcade.color.BLACK,
    radius: float = 20.0,
    border_width: float = 1.0,
) -> None:
    x, y = where
    arcade.draw.circle.draw_circle_outline(
        x, y,
        radius,
        color=color,
        border_width=border_width
    )
    arcade.draw.draw_line(
        x, y - radius, x, y + radius,
        color=color, line_width=border_width)

    arcade.draw.draw_line(
        x - radius, y, x + radius, y,
        color=color, line_width=border_width)


class MyGame(arcade.Window):

    def add_field_row(self, label_text: str, widget: UIWidget) -> None:
        children = (
            arcade.gui.widgets.text.UITextArea(
                text=label_text,
                width=100,
                height=20,
                color=arcade.color.BLACK,
                font_size=12
            ),
            widget
        )
        row = UIBoxLayout(vertical=False, space_between=10, children=children)
        self.rows.add(row)

    def __init__(
            self,
            width: int = 1280,
            height: int = 720,
            grid_tile_px: int = 100
    ):

        super().__init__(width, height, "Collision Inspector")
        # why does this need a context again?
        self.nine_patch = NinePatchTexture(
            left=5, right=5, top=5, bottom=5, texture=TEX_GREY_PANEL_RAW)
        self.ui = UIManager()
        self.spritelist: SpriteList[Sprite] = arcade.SpriteList()


        textbox_template = dict(width=40, height=20, text_color=arcade.color.BLACK)
        self.cursor_x_field = UIInputText(
            text="1.0", **textbox_template).with_background(texture=self.nine_patch)

        self.cursor_y_field = UIInputText(
            text="1.0", **textbox_template).with_background(texture=self.nine_patch)

        self.rows = UIBoxLayout(space_between=20).with_background(color=arcade.color.GRAY)

        self.grid_tile_px = grid_tile_px
        self.ui.add(self.rows)

        self.add_field_row("Cursor Y", self.cursor_y_field)
        self.add_field_row("Cursor X", self.cursor_x_field)
        self.ui.enable()

        # for y in range(8):
        #     for x in range(12):
        #         sprite = SpriteSolidColor(grid_tile_px, grid_tile_px, color=arcade.color.WHITE)
        #         sprite.position = x * 101 + 50, y * 101 + 50
        #         self.spritelist.append(sprite)
        self.build_sprite_grid(8, 12, self.grid_tile_px, Vec2(50, 50))
        self.background_color = arcade.color.DARK_GRAY
        self.set_mouse_visible(False)
        self.cursor = 0, 0
        self.from_mouse = True
        self.on_widget = False

    def build_sprite_grid(
            self,
            columns: int,
            rows: int,
            grid_tile_px: int,
            offset: tuple[float, float] = (0, 0)
    ):
        offset_x, offset_y = offset
        self.spritelist.clear()

        for row in range(rows):
            x = offset_x + grid_tile_px * row
            for column in range(columns):
                y = offset_y + grid_tile_px * column
                sprite = SpriteSolidColor(grid_tile_px, grid_tile_px, color=arcade.color.WHITE)
                sprite.position = x, y
                self.spritelist.append(sprite)

    def on_update(self, dt: float = 1 / 60):
        self.cursor = Vec2(self.mouse["x"], self.mouse["y"])

        widgets = list(self.ui.get_widgets_at(self.cursor))
        on_widget = bool(len(widgets))

        if self.on_widget != on_widget:
            self.set_mouse_visible(on_widget)
            self.on_widget = on_widget

    def on_draw(self):
        self.clear()
        # Reset color
        for sprite in self.spritelist:
            sprite.color = arcade.color.WHITE
            # sprite.angle += 0.2

        # Mark hits
        hits = arcade.get_sprites_at_point(self.cursor, self.spritelist)
        for hit in hits:
            hit.color = arcade.color.BLUE

        self.spritelist.draw()
        self.spritelist.draw_hit_boxes(color=arcade.color.GREEN)
        if hits:
            arcade.draw.rect.draw_rect_outline(rect=hits[0].rect, color=arcade.color.RED)
        if not self.on_widget:
            draw_crosshair(self.cursor)

        self.ui.draw()

MyGame().run()