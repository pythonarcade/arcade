import pytest
import arcade.color
from arcade.gui import Theme
from arcade.gui import Font


def test_theme_font():
    theme = Theme()
    assert isinstance(theme.font, Font)

    assert theme.font.color == Font.DEFAULT_COLOR
    assert theme.font.size == Font.DEFAULT_SIZE
    assert theme.font.name == Font.DEFAULT_NAME

    theme.font.size = 10
    theme.font.color = arcade.color.WHITE
    theme.font.name = "verdana"
    assert theme.font.color == arcade.color.WHITE
    assert theme.font.size == 10
    assert theme.font.name == "verdana"

    theme.font.size = 12
    theme.font.name = Font.DEFAULT_NAME
    assert theme.font.name == Font.DEFAULT_NAME


def test_theme_set_new_font_ban():
    theme = Theme()
    theme_font = theme.font
    new_font = Font()

    with pytest.raises(Exception):
        theme.font = new_font

    assert theme.font is theme_font


def test_theme_delete_font_ban():
    theme = Theme()
    theme_font = theme.font

    with pytest.raises(Exception):
        del theme.font

    assert theme.font is theme_font


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
