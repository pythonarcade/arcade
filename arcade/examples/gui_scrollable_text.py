"""
If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gui_scrollable_text
"""
from arcade.gui.nine_patch import NinePatchTexture

import arcade
from arcade import load_texture
from arcade.gui import UIManager, UIInputText, UITextArea

LOREM_IPSUM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent eget pellentesque velit. "
    "Nam eu rhoncus nulla. Fusce ornare libero eget ex vulputate, vitae mattis orci eleifend. "
    "Donec quis volutpat arcu. Proin lacinia velit id imperdiet ultrices. Fusce porta magna leo, "
    "non maximus justo facilisis vel. Duis pretium sem ut eros scelerisque, a dignissim ante "
    "pellentesque. Cras rutrum aliquam fermentum. Donec id mollis mi.\n"
    "\n"
    "Nullam vitae nunc aliquet, lobortis purus eget, porttitor purus. Curabitur feugiat purus sit "
    "amet finibus accumsan. Proin varius, enim in pretium pulvinar, augue erat pellentesque ipsum, "
    "sit amet varius leo risus quis tellus. Donec posuere ligula risus, et scelerisque nibh cursus "
    "ac. Mauris feugiat tortor turpis, vitae imperdiet mi euismod aliquam. Fusce vel ligula volutpat, "
    "finibus sapien in, lacinia lorem. Proin tincidunt gravida nisl in pellentesque. Aenean sed "
    "arcu ipsum. Vivamus quam arcu, elementum nec auctor non, convallis non elit. Maecenas id "
    "scelerisque lectus. Vivamus eget sem tristique, dictum lorem eget, maximus leo. Mauris lorem "
    "tellus, molestie eu orci ut, porta aliquam est. Nullam lobortis tempor magna, egestas lacinia lectus.\n"
)


class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "Scrollable Text", resizable=True)
        self.manager = UIManager()
        self.manager.enable()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        bg_tex = NinePatchTexture(
            start=(5, 5),
            end=(95, 95),
            texture=load_texture(":resources:gui_basic_assets/window/grey_panel.png"))
        text_area = UITextArea(
            x=100,
            y=200,
            width=200,
            height=300,
            text=LOREM_IPSUM,
            text_color=(0, 0, 0, 255),
        )

        self.manager.add(text_area.with_padding(all=15).with_background(texture=bg_tex))

        self.manager.add(
            UIInputText(x=340, y=200, width=200, height=50, text="Hello")
            .with_background(texture=bg_tex)
            .with_padding(all=10)
        )

        self.manager.add(
            UIInputText(x=340, y=110, width=200, height=50, text="").with_border(),
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()


window = MyWindow()
arcade.run()
