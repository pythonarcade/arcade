"""Tests for the labels arcade.draw_text keeps and reuses."""

import pytest

import arcade
from arcade import text as text_module

# These tests call draw_text on purpose, which warns that it's slow
pytestmark = pytest.mark.filterwarnings("ignore::arcade.exceptions.PerformanceWarning")


@pytest.fixture
def label_cache(window):
    cache = window.ctx.label_cache
    cache.clear()
    yield cache
    cache.clear()


def _render(window, draw):
    """Draw into an offscreen framebuffer and return its pixels"""
    ctx = window.ctx
    fbo = ctx.framebuffer(color_attachments=[ctx.texture((400, 300), components=4)])
    with fbo.activate():
        window.default_camera.use()
        fbo.clear(color=(0, 0, 0, 0))
        draw()
    return fbo.read(components=4)


def test_multiline_has_its_own_label(window, label_cache):
    """A multiline call and an otherwise equal single line call don't share a label"""
    text = "A long line of text that wraps when multiline"
    arcade.draw_text(text, 10, 10, width=200, multiline=True)
    arcade.draw_text(text, 10, 10, width=200, multiline=False)
    assert len(label_cache) == 2
    assert {label.multiline for label in label_cache.values()} == {True, False}


def test_rotation_reuses_label(window, label_cache):
    """Animating rotation updates one label instead of adding one per angle"""
    for frame in range(100):
        arcade.draw_text("Spin", 100, 100, rotation=frame * 0.7)
    assert len(label_cache) == 1
    (label,) = label_cache.values()
    assert label.rotation == pytest.approx(99 * 0.7)


def test_cache_size_is_limited(window, label_cache, monkeypatch):
    """The cache forgets the least recently used labels instead of growing forever"""
    # A small limit, since each new font size is slow to load
    limit = 5
    monkeypatch.setattr(text_module, "_DRAW_TEXT_CACHE_SIZE", limit)
    for frame in range(limit + 3):
        arcade.draw_text("Pulse", 100, 100, font_size=10 + frame)
    assert len(label_cache) == limit
    # The newest are kept and the oldest forgotten
    font_sizes = sorted(label.font_size for label in label_cache.values())
    assert font_sizes == [13, 14, 15, 16, 17]

    # Using a label makes it the most recent, so it's kept
    arcade.draw_text("Pulse", 100, 100, font_size=13)
    arcade.draw_text("Pulse", 100, 100, font_size=18)
    assert sorted(label.font_size for label in label_cache.values()) == [13, 15, 16, 17, 18]


def _draw_hud(changing_text):
    lines = ["Lives: 3", "Level: 7", changing_text, "Coins: 42", "Best: 9001"]
    for i, line in enumerate(lines):
        arcade.draw_text(line, 10, 10 + i * 24, arcade.color.WHITE, 16)


def test_same_style_lines_keep_their_labels(window, label_cache):
    """Several lines in the same style each keep a label, even if one keeps changing"""
    _draw_hud("Time: 0")
    static_labels = {key[1]: label for key, label in label_cache.items()}
    for frame in range(1, 30):
        _draw_hud(f"Time: {frame}")

    # The unchanging lines still use their original labels
    for text, label in static_labels.items():
        if not text.startswith("Time"):
            assert label_cache[next(key for key in label_cache if key[1] == text)] is label
    # The changing line doesn't add a label every frame
    assert len(label_cache) <= text_module._DRAW_TEXT_LABELS_PER_STYLE
    assert any(key[1] == "Time: 29" for key in label_cache)


def test_reused_label_draws_correctly(window, label_cache):
    """Drawing many texts in one style matches drawing separate Text objects"""
    lines = [(f"Line {i}: {'abcdefghij'[i:]}", 20 + i * 7, 20 + i * 40) for i in range(10)]
    texts = [arcade.Text(text, x, y, arcade.color.WHITE, 16) for text, x, y in lines]

    def via_draw_text():
        for text, x, y in lines:
            arcade.draw_text(text, x, y, arcade.color.WHITE, 16)

    def via_text_objects():
        for text in texts:
            text.draw()

    for _ in range(3):
        drawn = _render(window, via_draw_text)
    assert drawn == _render(window, via_text_objects)
    assert any(drawn)
