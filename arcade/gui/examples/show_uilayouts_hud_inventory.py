from typing import Optional, Dict

from PIL.Image import Image, ANTIALIAS

import arcade
from arcade import View, Window, load_texture, Texture
from arcade.gui import UIImageButton
from arcade.gui.elements.box import UIColorBox
from arcade.gui.layouts.box import UIBoxLayout
from arcade.gui.layouts.manager import UILayoutManager

SLOT_TEXTURE = load_texture(":resources:gui_basic_assets/button_square_blue.png")
SLOT_TEXTURE_PRESSED = load_texture(
    ":resources:gui_basic_assets/button_square_blue_pressed.png"
)

ITEMS = {
    "Sword": load_texture(":resources:gui_basic_assets/items/sword_gold.png"),
    "Shield": load_texture(":resources:gui_basic_assets/items/shield_gold.png"),
}


class SlotButton(UIImageButton):
    def __init__(self, game_state: Dict, item: str):
        # Combine slot background with slot image
        slot_tex = self.combine_textures(ITEMS.get(item), SLOT_TEXTURE)
        slot_tex_pressed = self.combine_textures(
            ITEMS.get(item), SLOT_TEXTURE_PRESSED, offset_y=4
        )
        super().__init__(
            normal_texture=slot_tex,
            press_texture=slot_tex_pressed,
        )

        self.game_state = game_state
        self.item = item

    def on_click(self):
        self.game_state["equipped_item"] = self.item

    @staticmethod
    def combine_textures(fg: Optional[Texture], bg: Optional[Texture], offset_y=0):
        if fg is None:
            return bg
        if bg is None:
            return fg

        img_fg: Image = fg.image
        img_bg: Image = bg.image

        thumbnail_size = int(img_bg.width * 0.8)
        img_fg = img_fg.resize((thumbnail_size, thumbnail_size), ANTIALIAS)

        combined_img = img_bg.copy()
        offset = (
            (img_bg.width - img_fg.width) // 2,
            (img_bg.width - img_fg.width) // 2 + offset_y,
        )
        combined_img.paste(img_fg, box=offset, mask=img_fg.convert("RGBA"))
        return Texture(fg.name + bg.name, combined_img, hit_box_algorithm="None")


class MyView(View):
    def __init__(self, window=None):
        super().__init__(window=window)
        self.ui_manager = UILayoutManager(window=window)

        # Init game state
        self.game_state = dict(equipped_item=None)

        # Equipped item
        self.equipped_item = UIColorBox(
            color=(0, 0, 0, 0), min_size=(100, 100)
        )  # Blank box while no item equid
        self._no_item_equipped = self.equipped_item.texture
        self.ui_manager.pack(self.equipped_item, center_x=0, center_y=0)

        # Create inventory
        inventory = UIBoxLayout(
            vertical=False,
            bg=(151, 113, 74),
            border_color=(136, 102, 68),
            border_width=3,
            padding=5,
        )
        self.ui_manager.pack(inventory, center_x=0, bottom=0)

        items = ["Sword", "Shield", None, None]
        for item in items:
            inventory.pack(SlotButton(self.game_state, item), space=20)

        # manually call `do_layout()`, so everything is ready on the first `on_draw()` call
        self.ui_manager.do_layout()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)
        self.ui_manager.enable()

    def on_update(self, delta_time: float):
        # Update equipped item from game state
        item_tex = ITEMS.get(self.game_state["equipped_item"])
        if item_tex:
            self.equipped_item.texture = item_tex
        else:
            self.equipped_item.texture = self._no_item_equipped

    def on_draw(self):
        arcade.start_render()
        self.ui_manager.on_draw()


def main():
    window = Window(resizable=True)
    window.show_view(MyView())
    arcade.run()


if __name__ == "__main__":
    main()
