import arcade
from arcade.examples.perf_test.stress_test_draw_shapes import FPSCounter
from arcade.gui import UIManager
from arcade.gui.constructs import OKMessageBox



class UIMockup(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        self.manager = UIManager()
        self.manager.enable()
        self.fps = FPSCounter()
        arcade.set_background_color(arcade.color.COOL_GREY)

        self.manager.add(
            OKMessageBox(
                width=300,
                height=200,
                text=(
                    "You should have a look on the new GUI features "
                    "coming up with arcade 2.6!"
                ))
        )

    def on_draw(self):
        self.fps.tick()
        arcade.start_render()
        self.manager.draw()


window = UIMockup()
arcade.run()
