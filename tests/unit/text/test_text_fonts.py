"""Tests for font names, paths to font files, and lists of them"""

import pytest

import arcade
import arcade.text
import pyglet

KENNEY = "Kenney Future"
KENNEY_HANDLE = ":system:fonts/ttf/Kenney/Kenney_Future.ttf"


@pytest.fixture
def font_families(monkeypatch) -> dict:
    """Forget which font files were loaded, so each test starts fresh"""
    families: dict = {}
    monkeypatch.setattr(arcade.text, "_font_file_families", families, raising=False)
    return families


def _render(window, text: arcade.Text):
    """Draw a Text into an offscreen framebuffer and return its pixels"""
    ctx = window.ctx
    fbo = ctx.framebuffer(color_attachments=[ctx.texture((400, 100), components=4)])
    with fbo.activate():
        fbo.clear(color=(0, 0, 0, 0))
        text.draw()
    return fbo.read(components=4)


def _make(font_name) -> arcade.Text:
    return arcade.Text("Hello World", 10, 30, font_name=font_name, font_size=30)


def _paths() -> list:
    path = arcade.resources.resolve(KENNEY_HANDLE)
    return [KENNEY_HANDLE, str(path)]


@pytest.mark.parametrize("font_name", _paths())
def test_path_uses_the_font_in_the_file(window, font_families, font_name):
    text = _make(font_name)
    assert text.label.font_name == KENNEY
    assert _render(window, text) == _render(window, _make(KENNEY))


@pytest.mark.parametrize("font_name", _paths())
def test_font_name_setter_accepts_path(window, font_families, font_name):
    text = _make("Liberation Sans")
    text.font_name = font_name
    assert text.label.font_name == KENNEY
    assert _render(window, text) == _render(window, _make(KENNEY))


def test_path_in_list(window, font_families):
    text = _make(("NoSuchFontXYZ", KENNEY_HANDLE, "Liberation Sans"))
    assert text.label.font_name == KENNEY


def test_first_available_font_is_used(window, font_families):
    assert _make(("NoSuchFontXYZ", "Liberation Sans", KENNEY)).label.font_name == "Liberation Sans"
    assert _make(("Liberation Sans", KENNEY_HANDLE)).label.font_name == "Liberation Sans"


def test_missing_resource_falls_back_to_next_name(window, font_families):
    text = _make((":resources:fonts/ttf/NoSuchFont.ttf", "Liberation Sans"))
    assert text.label.font_name == "Liberation Sans"


def test_unknown_resource_handle_raises(window, font_families):
    with pytest.raises(KeyError):
        _make(":nosuchhandle:fonts/NoSuchFont.ttf")


def test_list_of_names(window, font_families):
    text = _make(["NoSuchFontXYZ", "Liberation Sans"])  # type: ignore
    assert text.label.font_name == "Liberation Sans"


# Tests draw_text, which warns that it's slow
@pytest.mark.filterwarnings("ignore::arcade.exceptions.PerformanceWarning")
def test_draw_text_list_and_path(window, font_families):
    window.ctx.label_cache.clear()
    arcade.draw_text("Hello", 10, 10, font_name=["NoSuchFontXYZ", "Liberation Sans"])  # type: ignore
    arcade.draw_text("Hello", 10, 10, font_name=KENNEY_HANDLE)
    fonts = sorted(text.label.font_name for text in window.ctx.label_cache.values())
    assert fonts == [KENNEY, "Liberation Sans"]


def test_each_file_is_loaded_once(window, font_families, monkeypatch):
    added = []
    add_file = pyglet.font.add_file

    def counting_add_file(path):
        added.append(path)
        add_file(path)

    monkeypatch.setattr(pyglet.font, "add_file", counting_add_file)
    for _ in range(3):
        _make(KENNEY_HANDLE)
    arcade.load_font(KENNEY_HANDLE)
    assert len(added) == 1


def test_file_loaded_elsewhere(window, font_families):
    """A file already added to pyglet directly reports no new fonts, so the
    family name is read from the file"""
    path = arcade.resources.resolve(KENNEY_HANDLE)
    pyglet.font.add_file(str(path))
    assert _make(str(path)).label.font_name == KENNEY
    assert font_families[path] == KENNEY


def test_load_font_then_name(window, font_families):
    arcade.load_font(KENNEY_HANDLE)
    assert _make(KENNEY).label.font_name == KENNEY


def test_empty_name_raises(window, font_families):
    with pytest.raises(ValueError):
        _make("")
    with pytest.raises(ValueError):
        _make(())
