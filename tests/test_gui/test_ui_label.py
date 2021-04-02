from arcade.gui import UILabel


def test_ui_element_renders_on_style_change_with_own_id():
    label = UILabel(
        text="(should be size 40 text)", center_x=200, center_y=200, id="label_3"
    )
    width_with_default_font = label.width

    label.set_style_attrs(font_size=40)

    assert label.width > width_with_default_font
