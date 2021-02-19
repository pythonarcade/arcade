from typing import Optional, Dict

from PIL.Image import Image, ANTIALIAS

import arcade
from arcade import View, Window, load_texture, Texture
from arcade.gui import UIImageButton, UIFlatButton
from arcade.gui.elements.box import UIBox
from arcade.gui.layouts.anchor import UIAnchorLayout
from arcade.gui.layouts.box import UIBoxLayout
from arcade.gui.layouts.manager import UILayoutManager

SLOT_TEXTURE = load_texture(':resources:gui_basic_assets/button_square_blue.png')
SLOT_TEXTURE_PRESSED = load_texture(':resources:gui_basic_assets/button_square_blue_pressed.png')

ITEMS = {
    'Sword': load_texture(':resources:gui_basic_assets/items/sword_gold.png'),
    'Shield': load_texture(':resources:gui_basic_assets/items/shield_gold.png'),
}


class SlotButton(UIImageButton):

    def __init__(self, game_state: Dict, item: str):
        # Combine slot background with slot image
        slot_tex = self.combine_textures(ITEMS.get(item), SLOT_TEXTURE)
        slot_tex_pressed = self.combine_textures(ITEMS.get(item), SLOT_TEXTURE_PRESSED, offset_y=4)
        super().__init__(
            normal_texture=slot_tex,
            press_texture=slot_tex_pressed,
        )

        self.game_state = game_state
        self.item = item

    def on_click(self):
        self.game_state['equipped_item'] = self.item

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
        offset = ((img_bg.width - img_fg.width) // 2, (img_bg.width - img_fg.width) // 2 + offset_y)
        combined_img.paste(img_fg, box=offset, mask=img_fg.convert('RGBA'))
        return Texture(fg.name + bg.name, combined_img, hit_box_algorithm='None')


class MyView(View):
    def __init__(self, window=None):
        super().__init__(window=window)
        self.ui_manager = UILayoutManager(window=window)

        # Init game state
        self.game_state = dict(
            equipped_item=None
        )

        show_inventory = UIFlatButton('Inventory', width=150, height=50)
        self.ui_manager.pack(show_inventory, center_x=0, center_y=0)
        show_inventory.on_click = self.create_inventory

        self.equipped_item = UIBox(100, 100, arcade.color.LIGHT_GRAY)

    def create_inventory(self):
        # Build inventory
        frame = UIAnchorLayout(400, 310, bg=arcade.color.BROWN)

        # fix size
        frame.min_size = None
        frame.size_hint = None

        self.ui_manager.pack(frame, center_x=0, center_y=0)

        # Inventory with slots
        inventory = UIBoxLayout(vertical=True, id=f'col')
        frame.pack(inventory, left=0, top=0, bg_color=arcade.color.BROWN)

        # Add slots
        items = ['Sword', 'Shield', None, None, None, None, None, None, None, None, None, None, None, None, None, None]

        ci = iter(items)
        space = 10
        for y in range(4):
            row = inventory.pack(UIBoxLayout(vertical=False, id=f'row-{y}'), space=space)
            for x in range(4):
                row.pack(SlotButton(self.game_state, next(ci)), space=space)

        # Active item
        self.equipped_item = UIBox(100, 100, arcade.color.LIGHT_GRAY)
        frame.pack(self.equipped_item, top=10, right=10)
        self._no_item_equipped = self.equipped_item.texture

        # Close button
        close_btn = UIFlatButton('Close', width=100, height=35)
        frame.pack(close_btn, bottom=10, right=10)

        @close_btn.event()
        def on_click():
            self.ui_manager.remove(frame)

        # manually call `do_layout()`, so everything is ready on the first `on_draw()` call
        self.ui_manager.do_layout()

        self.inv = inventory

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)

    def on_update(self, delta_time: float):
        # Update equipped item from game state
        item_tex = ITEMS.get(self.game_state['equipped_item'])
        if item_tex:
            self.equipped_item.texture = item_tex
        else:
            self.equipped_item.texture = SLOT_TEXTURE

    def on_draw(self):
        arcade.start_render()
        self.ui_manager.on_draw()


def main():
    window = Window(resizable=True)
    window.show_view(MyView())
    arcade.run()


if __name__ == '__main__':
    main()
