"""get_display_size() is in window units, so a window that size fills the screen (#2791)."""

import pyglet
import pytest

import arcade


class FakeScreen:
    def __init__(self, width, height, scale):
        self.width = width
        self.height = height
        self._scale = scale

    def get_scale(self):
        return self._scale


@pytest.fixture
def fake_screen(monkeypatch):
    def use(width, height, scale, dpi_scaling, platform):
        screen = FakeScreen(width, height, scale)

        class FakeDisplay:
            def get_screens(self):
                return [screen]

        monkeypatch.setattr(pyglet.display, "Display", FakeDisplay)
        monkeypatch.setattr(pyglet.options, "dpi_scaling", dpi_scaling)
        monkeypatch.setattr(pyglet, "compat_platform", platform)

    return use


@pytest.mark.parametrize("platform", ["win32", "linux", "linux-compat"])
@pytest.mark.parametrize(
    ("width", "height", "scale", "expected"),
    [
        (1920, 1080, 1.0, (1920, 1080)),
        (2560, 1440, 1.25, (2048, 1152)),
        (1920, 1080, 1.5, (1280, 720)),
        # Rounded down, so the scaled window isn't bigger than the screen
        (1366, 768, 1.75, (780, 438)),
    ],
)
def test_stretch_divides_by_scale(fake_screen, platform, width, height, scale, expected):
    fake_screen(width, height, scale, "stretch", platform)
    size = arcade.get_display_size()
    assert size == expected
    assert int(size[0] * scale) <= width
    assert int(size[1] * scale) <= height


@pytest.mark.parametrize("platform", ["darwin", "emscripten"])
def test_stretch_on_platforms_that_dont_scale_windows(fake_screen, platform):
    fake_screen(1440, 900, 2.0, "stretch", platform)
    assert arcade.get_display_size() == (1440, 900)


def test_platform_scaling_returns_the_screen_size(fake_screen):
    fake_screen(2560, 1440, 1.25, "platform", "win32")
    assert arcade.get_display_size() == (2560, 1440)
