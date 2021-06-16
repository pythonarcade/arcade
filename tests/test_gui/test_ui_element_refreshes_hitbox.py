import pytest
from PIL import Image

from arcade import Texture
from arcade.gui import UIElement, UIStyle


@pytest.fixture()
def ui_element():
    return UIElement(
        center_x=0,
        center_y=0,
        min_size=None,
        size_hint=None,
        id=None,
        style=UIStyle.default_style(),
    )


def test_sprite_refreshes_hitbox_after_switching_texture(ui_element):
    tex_1 = Texture("tex1", Image.new("RGBA", (50, 50), (0, 0, 0, 1)))
    tex_2 = Texture("tex2", Image.new("RGBA", (100, 100), (0, 0, 0, 1)))

    ui_element.texture = tex_1

    assert ui_element.get_adjusted_hit_box() == [
        [-25.0, -25.0],
        [25.0, -25.0],
        [25.0, 25.0],
        [-25.0, 25.0],
    ]

    ui_element.texture = tex_2

    assert ui_element.get_adjusted_hit_box() == [
        [-50.0, -50.0],
        [50.0, -50.0],
        [50.0, 50.0],
        [-50.0, 50.0],
    ]


def test_sprite_refreshes_hitbox_after_changing_width(ui_element: UIElement):
    tex_1 = Texture("tex1", Image.new("RGBA", (50, 50), (0, 0, 0, 1)))
    ui_element.position = 200, 200

    ui_element.texture = tex_1

    ui_element.width = 100
    assert ui_element.get_adjusted_hit_box() == [
        [150.0, 175.0],
        [250.0, 175.0],
        [250.0, 225.0],
        [150.0, 225.0],
    ]


def test_sprite_refreshes_hitbox_after_resize_texture(ui_element):
    tex_1 = Texture("tex1", Image.new("RGBA", (50, 50), (0, 0, 0, 1)))

    ui_element.texture = tex_1

    assert ui_element.get_adjusted_hit_box() == [
        [-25.0, -25.0],
        [25.0, -25.0],
        [25.0, 25.0],
        [-25.0, 25.0],
    ]

    ui_element.width = 100
    ui_element.height = 100
    assert ui_element.get_adjusted_hit_box() == [
        [-50.0, -50.0],
        [50.0, -50.0],
        [50.0, 50.0],
        [-50.0, 50.0],
    ]


def test_sprite_refreshes_hitbox_after_scale(ui_element):
    tex_1 = Texture("tex1", Image.new("RGBA", (50, 50), (0, 0, 0, 1)))

    ui_element.texture = tex_1

    assert ui_element.get_adjusted_hit_box() == [
        [-25.0, -25.0],
        [25.0, -25.0],
        [25.0, 25.0],
        [-25.0, 25.0],
    ]

    ui_element.scale = 2
    assert ui_element.get_adjusted_hit_box() == [
        [-50.0, -50.0],
        [50.0, -50.0],
        [50.0, 50.0],
        [-50.0, 50.0],
    ]
