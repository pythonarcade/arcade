"""Liberation Sans is the default font, loaded the first time it's used (#1135)."""

import arcade
from arcade.gui import UIInputText, UILabel, UITextArea


def test_text_default_font(window):
    text = arcade.Text("Hello", 0, 0)
    # The name of the font that was found
    assert text.font_name == "Liberation Sans"


def test_default_font_bold_and_italic(window):
    font = arcade.Text("Hello", 0, 0, bold=True, italic=True)._label.document.get_font()
    assert font.name == "Liberation Sans"
    assert font.weight == "bold"
    assert font.style == "italic"


def test_create_text_sprite_default_font(window):
    sprite = arcade.create_text_sprite("Hello")
    assert sprite.width > 0


def test_liberation_families_load_when_used(window, monkeypatch):
    # tests/conftest.py loads the Liberation fonts for every test, so record
    # which files using a name asks for instead
    loaded = []
    real_load = arcade.text._load_font_file

    def record(path):
        loaded.append(path.name)
        return real_load(path)

    monkeypatch.setattr(arcade.text, "_load_font_file", record)
    arcade.Text("x", 0, 0, font_name="liberation mono")
    assert loaded == [
        f"Liberation_Mono_{style}.ttf" for style in ("Regular", "Bold", "Italic", "BoldItalic")
    ]

    loaded.clear()
    arcade.Text("x", 0, 0, font_name="Arial")
    assert loaded == []


def test_gui_text_widgets_default_font(window):
    assert UILabel(text="x").font_name == "Liberation Sans"
    assert UITextArea(text="x").doc.get_style("font_name", 0) == "Liberation Sans"
    assert UIInputText(text="x").doc.get_style("font_name", 0) == "Liberation Sans"


def test_gui_text_widgets_take_font_file_paths(window):
    path = ":resources:fonts/ttf/Kenney/Kenney_Pixel.ttf"
    assert UITextArea(text="x", font_name=path).doc.get_style("font_name", 0) == "Kenney Pixel"
    assert UIInputText(text="x", font_name=path).doc.get_style("font_name", 0) == "Kenney Pixel"
