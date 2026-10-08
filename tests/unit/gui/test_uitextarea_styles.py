"""UITextArea's style arguments, and styles set in ATTRIBUTED and HTML text (#2441)."""

import arcade
from arcade.gui import UITextArea

RED = arcade.types.Color(255, 0, 0, 255)
BLUE = arcade.types.Color(0, 0, 255, 255)


def test_bold_and_italic(window):
    area = UITextArea(text="hello", bold=True, italic=True)
    assert area.doc.get_style("weight", 0) == "bold"
    assert area.doc.get_style("style", 0) == "italic"
    font = area.doc.get_font(0)
    assert font.weight == "bold"
    assert font.style == "italic"


def test_plain_text_uses_the_arguments(window):
    area = UITextArea(text="hello", font_size=20, text_color=BLUE)
    assert area.doc.get_style("font_size", 4) == 20
    assert area.doc.get_style("color", 4) == BLUE


def test_attributed_text_keeps_its_styles(window):
    area = UITextArea(
        text="{color (255, 0, 0, 255)}red{color None} blue",
        document_mode="ATTRIBUTED",
        text_color=BLUE,
        font_size=20,
    )
    assert area.doc.text == "red blue"
    # Set in the text
    assert area.doc.get_style("color", 0) == RED
    # Not set in the text, so the arguments apply
    assert area.doc.get_style("color", 5) == BLUE
    assert area.doc.get_style("font_size", 0) == 20


def test_html_text_keeps_its_styles(window):
    area = UITextArea(
        text='<b>bold</b> plain <font color="#ff0000">red</font>',
        document_mode="HTML",
        font_name=("Arial",),
        font_size=20,
        text_color=BLUE,
    )
    assert area.doc.get_style("weight", 0) == "bold"
    assert area.doc.get_style("weight", 6) == "normal"
    # The arguments replace the HTML decoder's own defaults
    assert area.doc.get_style("font_name", 6) == ("Arial",)
    assert area.doc.get_style("font_size", 6) == 20
    assert area.doc.get_style("color", 6) == BLUE
    # A color set in the HTML wins
    assert tuple(area.doc.get_style("color", 12)) == tuple(RED)
