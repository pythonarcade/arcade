"""
User Interface Tutorial
"""
import arcade
from arcade import View, Window
from arcade.gui import UILabel
from arcade.gui.layouts.box import UIBoxLayout
from arcade.gui.layouts.manager import UILayoutManager


class MyView(View):
    """ Main program view """

    def __init__(self, window=None):
        """ Set up this view """
        super().__init__(window=window)
        # Create a UI manager to handle layout
        self.ui_manager = UILayoutManager(window=window)

    def on_show_view(self):
        """
        Our main view
        """
        # Set out background color
        arcade.set_background_color(arcade.color.ARSENIC)

        # This needs docs/explanation
        root_layout = self.ui_manager.root_layout

        # This needs docs/explanation
        layout_top_left = UIBoxLayout(id="top left",
                                      padding=5,
                                      border_color=arcade.color.GRAY)

        layout_top_left.pack(UILabel(text="Label 1"))
        layout_top_left.pack(UILabel(text="Label 2"))

        # Space. What is space? Margin? Passing? On all sides? Just one?
        layout_top_left.pack(UILabel(text="Another label, space=20"), space=20)

        # This must pack things. I'm guessing.
        root_layout.pack(layout_top_left, top=0, left=20, fill_x=True)

    def on_draw(self):
        """ Draw the view screen. """
        arcade.start_render()

        # Draw the UI. Draw last so it draws over everything else.
        self.ui_manager.on_draw()


def main():
    """ Main method. Eveything starts here. """
    window = Window(resizable=True)

    view = MyView()
    window.show_view(view)

    arcade.run()


if __name__ == "__main__":
    main()
