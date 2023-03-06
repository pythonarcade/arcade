"""
Menu.
"""
import arcade
import arcade.gui

# Screen title and size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Making a Menu"


class MainView(arcade.View):
    """ Main application class. """
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
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Enable the UIManager when the view is showm. 
        self.manager.enable()

    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        self.clear()

        # Draw the manager.
        self.manager.draw()


class MenuView(arcade.View):
    def __init__(self, main_view):
        super().__init__()

        self.manager = arcade.gui.UIManager()

        resume_button = arcade.gui.UIFlatButton(text="Resume", width=150)
        start_new_game_button = arcade.gui.UIFlatButton(text="Start New Game", width=150)
        volume_button = arcade.gui.UIFlatButton(text="Volume", width=150)
        options_button = arcade.gui.UIFlatButton(text="Options", width=150)

        exit_button = arcade.gui.UIFlatButton(text="Exit", width=320)

        # Initialise a grid in which widgets can be arranged.
        self.grid = arcade.gui.UIGridLayout(column_count=2, row_count=3, horizontal_spacing=20, vertical_spacing=20)

        # Adding the buttons to the layout.
        self.grid.add(resume_button, col_num=0, row_num=0)
        self.grid.add(start_new_game_button, col_num=1, row_num=0)
        self.grid.add(volume_button, col_num=0, row_num=1)
        self.grid.add(options_button, col_num=1, row_num=1)
        self.grid.add(exit_button, col_num=0, row_num=2, col_span=2)

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
            volume_menu = SubMenu("Volume Menu", "Enable Sound", ["Play: Rock", "Play: Punk", "Play: Pop"], "Adjust Volume")
            self.manager.add(volume_menu)

        @options_button.event("on_click")
        def on_click_options_button(event):
            options_menu = SubMenu("Funny Menu", "Fun?", ["Make Fun", "Enjoy Fun", "Like Fun"], "Adjust Fun")
            self.manager.add(options_menu)

    def on_hide_view(self):
        # Disable the UIManager when the view is hidden.
        self.manager.disable()

    def on_show_view(self):
        """ This is run once when we switch to this view """

        # Makes the background darker
        arcade.set_background_color([rgb - 50 for rgb in arcade.color.DARK_BLUE_GRAY])

        # Enable the UIManager when the view is showm. 
        self.manager.enable()

    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        self.clear()
        self.manager.draw()


class SubMenu(arcade.gui.UIMouseFilterMixin, arcade.gui.UIAnchorLayout):
    """Acts like a fake view/window."""
    def __init__(self, input_text_default: str, toggle_label: str, dropdown_options: list[str], slider_label: str):
        super().__init__(size_hint=(1, 1))

        # Setup frame which will act like the window.
        frame = self.add(arcade.gui.UIAnchorLayout(width=300, height=400, size_hint=None))
        frame.with_padding(all=20)

        # Add a background to the window.
        # Nine patch smoothes the edges.
        frame.with_background(texture=arcade.gui.NinePatchTexture(
            left=7,
            right=7,
            bottom=7,
            top=7,
            texture=arcade.load_texture(
                ":resources:gui_basic_assets/window/dark_blue_gray_panel.png"
            )
        ))

        back_button = arcade.gui.UIFlatButton(text="Back", width=250)
        # The event listener we used earlier for the button will not work here.
        back_button.on_click = self.on_click_back_button

        input_text = arcade.gui.UIInputText(text=input_text_default, width=250).with_border()
        # Adds a widget of the color DARK_BLUE_GRAY with height to separate the widgets
        # Its another method for adding space between widgets in a layout.
        space_20 = arcade.gui.UISpace(height=20, color=arcade.color.DARK_BLUE_GRAY)

        toggle_label = arcade.gui.UILabel(text=toggle_label)
        # Load the on-off textures. 
        on_texture = arcade.load_texture(":resources:gui_basic_assets/toggle/circle_switch_on.png")
        off_texture = arcade.load_texture(":resources:gui_basic_assets/toggle/circle_switch_off.png")

        toggle = arcade.gui.UITextureToggle(
            on_texture=on_texture,
            off_texture=off_texture,
            width=20,
            height=20
        )
        space_30 = arcade.gui.UISpace(height=30, color=arcade.color.DARK_BLUE_GRAY)

        dropdown = arcade.gui.UIDropdown(default=dropdown_options[0], options=dropdown_options, height=20, width=250)
        space_80 = arcade.gui.UISpace(height=80, color=arcade.color.DARK_BLUE_GRAY)

        slider_label = arcade.gui.UILabel(text=slider_label)
        pressed_style = arcade.gui.UISlider.UIStyle(filled_bar=arcade.color.GREEN, unfilled_bar=arcade.color.RED)
        default_style = arcade.gui.UISlider.UIStyle()
        style_dict = {"press": pressed_style, "normal": default_style, "hover": default_style, "disabled": default_style}
        # Configuring the styles is optional.
        slider = arcade.gui.UISlider(value=50, width=250, style=style_dict)
        space_70 = arcade.gui.UISpace(height=70, color=arcade.color.DARK_BLUE_GRAY)

        # Internal widget layout to handle widgets in this class.
        widget_layout = arcade.gui.UIBoxLayout(align="left")
        widget_layout.add(input_text)
        widget_layout.add(space_20)
        widget_layout.add(toggle_label)
        widget_layout.add(toggle)
        widget_layout.add(space_30)
        widget_layout.add(dropdown)
        widget_layout.add(space_80)
        widget_layout.add(slider_label)
        widget_layout.add(slider)
        widget_layout.add(space_70)
        widget_layout.add(back_button)

        frame.add(child=widget_layout, anchor_x="center_x", anchor_y="top")

    def on_click_back_button(self, event):
        # Removes the widget from the manager.
        # After this the manager will respond to its events like it previously did.
        self.parent.remove(self)


def main():
    """ Main function """

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    main_view = MainView()
    window.show_view(main_view)
    arcade.run()


if __name__ == "__main__":
    main()
