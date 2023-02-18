import arcade
from arcade import load_texture
from arcade.gui import UIManager, UIImage
from arcade.gui.events import UIOnChangeEvent
from arcade.gui.widgets.buttons import UIFlatButton, UITextureButton
from arcade.gui.widgets.layout import UIGridLayout, UIAnchorLayout
from arcade.gui.widgets.toggle import UITextureToggle


class UIMockup(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        self.manager = UIManager()
        self.manager.enable()
        self.background_color = arcade.color.DARK_BLUE_GRAY

        grid = UIGridLayout(
            column_count=3,
            row_count=4,
            size_hint=(0, 0),
            vertical_spacing=10,
            horizontal_spacing=10,
        )

        self.manager.add(UIAnchorLayout(children=[grid]))

        # simple UIFlatButton with text
        grid.add(UIFlatButton(text="UIFlatButton", width=200), row_num=0, col_num=0)

        # UIFlatButton change text placement right
        flat_with_more_text = UIFlatButton(text="text placed right", width=200)
        flat_with_more_text.place_text(anchor_x="right")
        grid.add(flat_with_more_text, row_num=1, col_num=0)

        # UIFlatButton change text placement right
        flat_with_more_text = UIFlatButton(text="text placed top left", width=200)
        flat_with_more_text.place_text(anchor_x="left", anchor_y="top")
        grid.add(flat_with_more_text, row_num=2, col_num=0)

        # UIFlatButton with icon on the left
        flat_with_icon_left = UIFlatButton(text="UIFlatButton with icon", width=200)
        flat_with_icon_left.place_text(align_x=+20)
        flat_with_icon_left.add(
            child=UIImage(
                texture=load_texture(":resources:gui_basic_assets/icons/larger.png"),
                width=30,
                height=30,
            ),
            anchor_x="left",
            align_x=10,
        )
        grid.add(flat_with_icon_left, row_num=0, col_num=1)

        # UIFlatButton with icon on the right
        flat_with_icon_right = UIFlatButton(text="UIFlatButton with icon", width=200)
        flat_with_icon_right.place_text(align_x=-20)
        flat_with_icon_right.add(
            child=UIImage(
                texture=load_texture(":resources:gui_basic_assets/icons/smaller.png"),
                width=30,
                height=30,
            ),
            anchor_x="right",
            align_x=-10,
        )
        grid.add(flat_with_icon_right, row_num=1, col_num=1)

        # UIFlatButton with icon on both sides
        flat_with_icon_right = UIFlatButton(text="UIFlatButton", width=200)
        flat_with_icon_right.add(
            child=UIImage(
                texture=load_texture(":resources:gui_basic_assets/icons/smaller.png"),
                width=30,
                height=30,
            ),
            anchor_x="left",
            align_x=10,
        )
        flat_with_icon_right.add(
            child=UIImage(
                texture=load_texture(":resources:gui_basic_assets/icons/smaller.png"),
                width=30,
                height=30,
            ),
            anchor_x="right",
            align_x=-10,
        )
        grid.add(flat_with_icon_right, row_num=2, col_num=1)

        # UITextureButton
        texture_button = UITextureButton(
            text="UITextureButton",
            width=200,
            texture=load_texture(":resources:gui_basic_assets/red_button_normal.png"),
            texture_hovered=load_texture(
                ":resources:gui_basic_assets/red_button_hover.png"
            ),
            texture_pressed=load_texture(
                ":resources:gui_basic_assets/red_button_press.png"
            ),
        )
        grid.add(texture_button, row_num=0, col_num=2)

        # UITextureButton with icon left
        texture_button_with_icon_left = UITextureButton(
            text="UITextureButton",
            width=200,
            texture=load_texture(":resources:gui_basic_assets/red_button_normal.png"),
            texture_hovered=load_texture(
                ":resources:gui_basic_assets/red_button_hover.png"
            ),
            texture_pressed=load_texture(
                ":resources:gui_basic_assets/red_button_press.png"
            ),
        )
        texture_button_with_icon_left.add(
            child=UIImage(
                texture=load_texture(":resources:gui_basic_assets/icons/smaller.png"),
                width=25,
                height=25,
            ),
            anchor_x="left",
            align_x=10,
        )
        grid.add(texture_button_with_icon_left, row_num=1, col_num=2)

        # UITextureButton with multiline text
        texture_button_with_icon_left = UITextureButton(
            text="UITextureButton\nwith a second line",
            width=200,
            texture=load_texture(":resources:gui_basic_assets/red_button_normal.png"),
            texture_hovered=load_texture(
                ":resources:gui_basic_assets/red_button_hover.png"
            ),
            texture_pressed=load_texture(
                ":resources:gui_basic_assets/red_button_press.png"
            ),
        )
        texture_button_with_icon_left.place_text(anchor_x="left", align_x=45)
        texture_button_with_icon_left.add(
            child=UIImage(
                texture=load_texture(":resources:gui_basic_assets/icons/smaller.png"),
                width=25,
                height=25,
            ),
            anchor_x="left",
            align_x=10,
        )
        grid.add(texture_button_with_icon_left, row_num=2, col_num=2)

        # UIFlatButtons with toggle
        texture_button_with_toggle = UIFlatButton(
            text="Just get crazy now!",
            width=630,
        )
        texture_button_with_toggle.place_text(anchor_x="left", align_x=45)
        texture_button_with_toggle.add(
            child=UIImage(
                texture=load_texture(":resources:gui_basic_assets/icons/smaller.png"),
                width=25,
                height=25,
            ),
            anchor_x="left",
            align_x=10,
        )
        toggle = texture_button_with_toggle.add(
            child=UITextureToggle(
                on_texture=load_texture(
                    ":resources:gui_basic_assets/toggle/switch_red.png"
                ),
                off_texture=load_texture(
                    ":resources:gui_basic_assets/toggle/switch_green.png"
                ),
                width=60,
                height=30,
            ),
            anchor_x="right",
            align_x=-10,
        )

        @toggle.event
        def on_change(event: UIOnChangeEvent):
            texture_button_with_toggle.disabled = event.new_value

        grid.add(texture_button_with_toggle, row_num=3, col_num=0, col_span=3)

    def on_draw(self):
        self.clear()
        self.manager.draw()


if __name__ == "__main__":
    window = UIMockup()
    arcade.run()
