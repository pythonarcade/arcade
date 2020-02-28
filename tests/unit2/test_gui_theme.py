import arcade.color
from arcade.gui import Theme


def test_theme_font():
    theme = Theme()
    assert theme.font_color == Theme.DEFAULT_FONT_COLOR
    assert theme.font_size == Theme.DEFAULT_FONT_SIZE
    assert theme.font_name == Theme.DEFAULT_FONT_NAME

    theme.set_font(10, arcade.color.WHITE, "verdana")
    assert theme.font_color == arcade.color.WHITE
    assert theme.font_size == 10
    assert theme.font_name == "verdana"

    theme.set_font(12, arcade.color.WENGE)
    assert theme.font_name == Theme.DEFAULT_FONT_NAME


def test_theme_box_texture():
    theme = Theme()
    assert theme.text_box_texture == ""

    theme.add_text_box_texture(
        ":resources:gui_themes/Fantasy/TextBox/Brown.png"
    )
    assert isinstance(theme.text_box_texture, arcade.Texture)


def test_theme_dialogut_box_texture():
    theme = Theme()
    assert theme.dialogue_box_texture == ""

    theme.add_dialogue_box_texture(
        ":resources:gui_themes/Fantasy/DialogueBox/DialogueBox.png"
    )
    assert isinstance(theme.dialogue_box_texture, arcade.Texture)


def test_theme_menu_texture():
    theme = Theme()
    assert theme.menu_texture == ""

    theme.add_menu_texture(
        ":resources:gui_themes/Fantasy/Menu/Menu.png"
    )
    assert isinstance(theme.menu_texture, arcade.Texture)


def test_theme_window_texture():
    theme = Theme()
    assert theme.window_texture == ""

    theme.add_window_texture(
        ":resources:gui_themes/Fantasy/Window/Window.png"
    )
    assert isinstance(theme.window_texture, arcade.Texture)


def test_theme_button_texture():
    theme = Theme()
    assert theme.button_textures == {"normal": "", "hover": "", "clicked": "", "locked": ""}

    theme.add_button_textures(
        ":resources:gui_themes/Fantasy/Buttons/Normal.png",
        ":resources:gui_themes/Fantasy/Buttons/Hover.png",
        ":resources:gui_themes/Fantasy/Buttons/Clicked.png",
        ":resources:gui_themes/Fantasy/Buttons/Locked.png"
    )

    for button_texture in theme.button_textures.values():
        assert isinstance(button_texture, arcade.Texture)

    theme.add_button_textures(
        ":resources:gui_themes/Fantasy/Buttons/Normal.png"
    )
    assert isinstance(theme.button_textures["normal"], arcade.Texture)
    assert theme.button_textures["normal"] is theme.button_textures["hover"]
    assert theme.button_textures["normal"] is theme.button_textures["clicked"]
    assert theme.button_textures["normal"] is theme.button_textures["locked"]
