"""
Menu.

Shows the usage of almost every gui widget, switching views and making a modal.
"""

from typing import List

import arcade
import arcade.gui

# Screen title and size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Making a Menu"


class MainView(arcade.View):
    """This is the class where your normal game would go."""

    def __init__(self):
        super().__init__()

        self.manager = arcade.gui.UIManager()

        switch_menu_button = arcade.gui.UIFlatButton(text="Pause", width=150)

        # Initialise the button with an on_click event.
        @switch_menu_button.event("on_click")
        def on_click_switch_button(event):
            # Passing the main view into menu view as an argument.
            menu_view = MenuView(self)
            self.window.show_view(menu_view)

        # Use the anchor to position the button on the screen.
        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=switch_menu_button,
        )

    def on_hide_view(self):
        # Disable the UIManager when the view is hidden.
        self.manager.disable()

    def on_show_view(self):
        """This is run once when we switch to this view"""
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Enable the UIManager when the view is showm.
        self.manager.enable()

    def on_draw(self):
        """Render the screen."""
        # Clear the screen
        self.clear()

        # Draw the manager.
        self.manager.draw()


class MenuView(arcade.View):
    """Main menu view class."""

    def __init__(self, main_view):
        super().__init__()

        self.manager = arcade.gui.UIManager()

        resume_button = arcade.gui.UIFlatButton(text="Resume", width=150)
        start_new_game_button = arcade.gui.UIFlatButton(text="Start New Game", width=150)
        volume_button = arcade.gui.UIFlatButton(text="Volume", width=150)
        options_button = arcade.gui.UIFlatButton(text="Options", width=150)

        exit_button = arcade.gui.UIFlatButton(text="Exit", width=320)

        # Initialise a grid in which widgets can be arranged.
        self.grid = arcade.gui.UIGridLayout(
            column_count=2, row_count=3, horizontal_spacing=20, vertical_spacing=20
        )

        # Adding the buttons to the layout.
        self.grid.add(resume_button, column=0, row=0)
        self.grid.add(start_new_game_button, column=1, row=0)
        self.grid.add(volume_button, column=0, row=1)
        self.grid.add(options_button, column=1, row=1)
        self.grid.add(exit_button, column=0, row=2, column_span=2)

        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.grid,
        )

        self.main_view = main_view

        @resume_button.event("on_click")
        def on_click_resume_button(event):
            # Pass already created view because we are resuming.
            self.window.show_view(self.main_view)

        @start_new_game_button.event("on_click")
        def on_click_start_new_game_button(event):
            # Create a new view because we are starting a new game.
            main_view = MainView()
            self.window.show_view(main_view)

        @exit_button.event("on_click")
        def on_click_exit_button(event):
            arcade.exit()

        @volume_button.event("on_click")
        def on_click_volume_button(event):
            volume_menu = SubMenu(
                "Volume Menu",
                "How do you like your volume?",
                "Enable Sound",
                ["Play: Rock", "Play: Punk", "Play: Pop"],
                "Adjust Volume",
            )
            self.manager.add(volume_menu, layer=1)

        @options_button.event("on_click")
        def on_click_options_button(event):
            options_menu = SubMenu(
                "Funny Menu",
                "Too much fun here",
                "Fun?",
                ["Make Fun", "Enjoy Fun", "Like Fun"],
                "Adjust Fun",
            )
            self.manager.add(options_menu, layer=1)

    def on_hide_view(self):
        # Disable the UIManager when the view is hidden.
        self.manager.disable()

    def on_show_view(self):
        """This is run once when we switch to this view"""

        # Makes the background darker
        arcade.set_background_color([rgb - 50 for rgb in arcade.color.DARK_BLUE_GRAY])

        # Enable the UIManager when the view is showm.
        self.manager.enable()

    def on_draw(self):
        """Render the screen."""
        # Clear the screen
        self.clear()
        self.manager.draw()


class SubMenu(arcade.gui.UIMouseFilterMixin, arcade.gui.UIAnchorLayout):
    """Acts like a fake view/window."""

    def __init__(
        self,
        title: str,
        input_text: str,
        toggle_label: str,
        dropdown_options: List[str],
        slider_label: str,
    ):
        super().__init__(size_hint=(1, 1))

        # Setup frame which will act like the window.
        frame = self.add(arcade.gui.UIAnchorLayout(width=300, height=400, size_hint=None))
        frame.with_padding(all=20)

        # Add a background to the window.
        # Nine patch smoothes the edges.
        frame.with_background(
            texture=arcade.gui.NinePatchTexture(
                left=7,
                right=7,
                bottom=7,
                top=7,
                texture=arcade.load_texture(
                    ":resources:gui_basic_assets/window/dark_blue_gray_panel.png"
                ),
            )
        )

        back_button = arcade.gui.UIFlatButton(text="Back", width=250)
        # The type of event listener we used earlier for the button will not work here.
        back_button.on_click = self.on_click_back_button

        title_label = arcade.gui.UILabel(text=title, align="center", font_size=20, multiline=False)
        # Adding some extra space around the title.
        title_label_space = arcade.gui.UISpace(height=30, color=arcade.color.DARK_BLUE_GRAY)

        input_text_widget = arcade.gui.UIInputText(text=input_text, width=250).with_border()

        # Load the on-off textures.
        on_texture = arcade.load_texture(
            ":resources:gui_basic_assets/simple_checkbox/circle_on.png"
        )
        off_texture = arcade.load_texture(
            ":resources:gui_basic_assets/simple_checkbox/circle_off.png"
        )

        # Create the on-off toggle and a label
        toggle_label = arcade.gui.UILabel(text=toggle_label)
        toggle = arcade.gui.UITextureToggle(
            on_texture=on_texture, off_texture=off_texture, width=20, height=20
        )

        # Align toggle and label horizontally next to each other
        toggle_group = arcade.gui.UIBoxLayout(vertical=False, space_between=5)
        toggle_group.add(toggle)
        toggle_group.add(toggle_label)

        # Create dropdown with a specified default.
        dropdown = arcade.gui.UIDropdown(
            default=dropdown_options[0], options=dropdown_options, height=20, width=250
        )

        slider_label = arcade.gui.UILabel(text=slider_label)
        pressed_style = arcade.gui.UISlider.UIStyle(
            filled_track=arcade.color.GREEN, unfilled_track=arcade.color.RED
        )
        default_style = arcade.gui.UISlider.UIStyle()
        style_dict = {
            "press": pressed_style,
            "normal": default_style,
            "hover": default_style,
            "disabled": default_style,
        }
        # Configuring the styles is optional.
        slider = arcade.gui.UISlider(value=50, width=250, style=style_dict)

        widget_layout = arcade.gui.UIBoxLayout(align="left", space_between=10)
        widget_layout.add(title_label)
        widget_layout.add(title_label_space)
        widget_layout.add(input_text_widget)
        widget_layout.add(toggle_group)
        widget_layout.add(dropdown)
        widget_layout.add(slider_label)
        widget_layout.add(slider)

        widget_layout.add(back_button)

        frame.add(child=widget_layout, anchor_x="center_x", anchor_y="top")

    def on_click_back_button(self, event):
        # Removes the widget from the manager.
        # After this the manager will respond to its events like it previously did.
        self.parent.remove(self)


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
    main_view = MainView()
    window.show_view(main_view)
    arcade.run()


if __name__ == "__main__":
    main()
