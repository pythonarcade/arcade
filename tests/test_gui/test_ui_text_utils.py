from pathlib import Path

import numpy as np
import pkg_resources
from PIL import Image

from arcade.gui import text_utils
from arcade.gui.text_utils import Padding


def img_diff(file1: Path, file2: Path) -> float:
    """Difference between two images in percent"""
    img_a = Image.open(file1).convert("RGB")
    img_b = Image.open(file2).convert("RGB")
    a = np.frombuffer(img_a.tobytes(), dtype="u1").astype("f4")
    b = np.frombuffer(img_b.tobytes(), dtype="u1").astype("f4")
    r = np.absolute(a - b)

    return np.sum(r) / np.sum(a)


def _find_expected_screen(title: str) -> Path:
    file = pkg_resources.resource_filename("tests.test_gui", f"assets/{title}.png")
    return Path(file)


def test_render_text():
    expected_screen = _find_expected_screen("test_render_text")
    actual_screen_path = expected_screen.with_name(
        f"{expected_screen.with_suffix('').name}_tmp.png"
    )

    # WHEN
    image, _ = text_utils.create_text(
        text="Hello Arcade, great joy with you.",
        font_name=("Arial"),
        font_size=16,
        font_color=(0, 0, 0),
        bg_color=(0, 100, 100),
        min_width=331,
        min_height=68,
        v_align="bottom",
        h_align="left",
        border_width=3,
        border_color=(255, 0, 0),
        padding=Padding(left=10),
    )
    image.save(str(actual_screen_path))

    # compare files
    assert (
        expected_screen.exists()
    ), f"expected screen missing, actual at {actual_screen_path}"

    assert (
        img_diff(expected_screen, actual_screen_path) < 0.135
    )  # max threshold for image difference, mac vs win
    actual_screen_path.unlink()


def test_render_raw_text():
    expected_screen = _find_expected_screen("test_render_raw_text")
    actual_screen_path = expected_screen.with_name(
        f"{expected_screen.with_suffix('').name}_tmp.png"
    )

    # WHEN
    image = text_utils.create_raw_text_image(
        text="Hello Arcade, great joy with you.",
        font_name=("Arial"),
        font_size=16,
        font_color=(0, 0, 0),
        bg_color=(0, 100, 100),
    )
    image.save(str(actual_screen_path))

    # compare files
    assert (
        expected_screen.exists()
    ), f"expected screen missing, actual at {actual_screen_path}"

    assert (
        img_diff(expected_screen, actual_screen_path) < 0.135
    )  # max threshold for image difference, mac vs win
    actual_screen_path.unlink()


def test_expand_ignores_bigger_images():
    # GIVEN
    image = Image.new("RGBA", (20, 30))

    # WHEN
    image = text_utils.expand(image, size=(10, 20), v_align="bottom", h_align="right")

    # THEN
    assert image.size == (20, 30)


def test_expand_text_image_align_bottom_right():
    expected_screen = _find_expected_screen("test_expand_text_image_align_bottom_right")
    actual_screen_path = expected_screen.with_name(
        f"{expected_screen.with_suffix('').name}_tmp.png"
    )

    # WHEN
    image = text_utils.create_raw_text_image(
        text="Hello Arcade, great joy with you.",
        font_name=("Arial"),
        font_size=16,
        font_color=(0, 0, 0),
        bg_color=(0, 100, 100),
    )
    image = text_utils.expand(image, size=(300, 50), v_align="bottom", h_align="right")

    image.save(str(actual_screen_path))

    # compare files
    assert (
        expected_screen.exists()
    ), f"expected screen missing, actual at {actual_screen_path}"

    assert (
        img_diff(expected_screen, actual_screen_path) < 0.135
    )  # max threshold for image difference, mac vs win
    actual_screen_path.unlink()


def test_expand_text_image_align_top_center():
    expected_screen = _find_expected_screen("test_expand_text_image_align_top_center")
    actual_screen_path = expected_screen.with_name(
        f"{expected_screen.with_suffix('').name}_tmp.png"
    )

    # WHEN
    image = text_utils.create_raw_text_image(
        text="Hello Arcade, great joy with you.",
        font_name=("Arial"),
        font_size=16,
        font_color=(0, 0, 0),
        bg_color=(0, 100, 100),
    )
    image = text_utils.expand(image, size=(300, 50), v_align="top", h_align="center")

    image.save(str(actual_screen_path))

    # compare files
    assert (
        expected_screen.exists()
    ), f"expected screen missing, actual at {actual_screen_path}"

    assert (
        img_diff(expected_screen, actual_screen_path) < 0.135
    )  # max threshold for image difference, mac vs win
    actual_screen_path.unlink()


def test_expand_text_image_align_center_left():
    expected_screen = _find_expected_screen("test_expand_text_image_align_center_left")
    actual_screen_path = expected_screen.with_name(
        f"{expected_screen.with_suffix('').name}_tmp.png"
    )

    # WHEN
    image = text_utils.create_raw_text_image(
        text="Hello Arcade, great joy with you.",
        font_name=("Arial"),
        font_size=16,
        font_color=(0, 0, 0),
        bg_color=(0, 100, 100),
    )
    image = text_utils.expand(image, size=(300, 50), v_align="center", h_align="left")

    image.save(str(actual_screen_path))

    # compare files
    assert (
        expected_screen.exists()
    ), f"expected screen missing, actual at {actual_screen_path}"

    assert (
        img_diff(expected_screen, actual_screen_path) < 0.135
    )  # max threshold for image difference, mac vs win
    actual_screen_path.unlink()
