import arcade
from arcade import linear
from arcade.gui import UIManager, TransitionChain, TransitionAttr, TransitionAttrIncr
from arcade.gui.transition import TransitionAttrSet
from arcade.gui.widgets.buttons import UIFlatButton


class DemoWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Init UIManager
        self.manager = UIManager()
        self.manager.enable()

        button = self.manager.add(UIFlatButton(text="Click me I can move!"))
        button.center_on_screen()

        @button.event
        def on_click(event):
            # button.disabled = True

            start_x, start_y = button.center
            chain = TransitionChain()

            chain.add(TransitionAttrSet(attribute="disabled", value=True, duration=0))

            chain.add(TransitionAttrIncr(
                attribute="center_x",
                increment=100,
                duration=1.0
            ))
            chain.add(TransitionAttrIncr(
                attribute="center_y",
                increment=100,
                duration=1,
                ease_function=linear
            ))

            # Go back
            chain.add(TransitionAttr(
                attribute="center_x",
                end=start_x,
                duration=1,
                ease_function=linear
            ))
            chain.add(TransitionAttr(
                attribute="center_y",
                end=start_y,
                duration=1,
                ease_function=linear
            ))
            chain.add(TransitionAttrSet(attribute="disabled", value=False, duration=0))

            button.add_transition(chain)

    def on_draw(self):
        self.clear()
        self.manager.draw()


if __name__ == "__main__":
    DemoWindow().run()
