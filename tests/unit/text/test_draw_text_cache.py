"""Tests for the labels arcade.draw_text keeps and reuses."""

import pytest

import arcade
from arcade import text as text_module
from arcade.clock import GLOBAL_CLOCK

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


def _next_frame():
    """The event loop ticks the clock once per frame"""
    GLOBAL_CLOCK.tick(1 / 60)


def _label_for(label_cache, text):
    return next(label for key, label in label_cache.items() if key[1] == text)


def test_same_style_lines_keep_their_labels(window, label_cache):
    """Several lines in the same style each keep a label, even if one keeps changing"""
    _draw_hud("Time: 0")
    labels = {key[1]: label for key, label in label_cache.items()}
    for frame in range(1, 30):
        _next_frame()
        _draw_hud(f"Time: {frame}")

    # The unchanging lines still use their original labels
    for text, label in labels.items():
        if not text.startswith("Time"):
            assert _label_for(label_cache, text) is label
    # The changing line keeps reusing its own label
    assert len(label_cache) == 5
    assert _label_for(label_cache, "Time: 29") is labels["Time: 0"]


@pytest.mark.parametrize("line_count", [9, 30])
def test_many_same_style_lines_keep_their_labels(window, label_cache, line_count):
    """There's no limit on lines per style: more than 8 used to take each other's labels"""

    def draw_lines():
        for i in range(line_count):
            arcade.draw_text(f"Line {i}", 10, 10 + i * 18)

    draw_lines()
    labels = dict(label_cache)
    for _ in range(5):
        _next_frame()
        draw_lines()
    assert len(label_cache) == line_count
    for key, label in labels.items():
        assert label_cache[key] is label


def test_line_that_stops_frees_its_label(window, label_cache):
    """A label not drawn in a frame is reused for a new line in the same style"""
    for text in ("Apple", "Banana", "Cherry"):
        arcade.draw_text(text, 10, 10)
    cherry = _label_for(label_cache, "Cherry")

    _next_frame()
    for text in ("Apple", "Banana", "Date"):
        arcade.draw_text(text, 10, 10)
    assert len(label_cache) == 3
    assert _label_for(label_cache, "Date") is cherry


def test_new_line_in_same_frame_gets_new_label(window, label_cache):
    """A label already drawn this frame isn't taken by another line"""
    arcade.draw_text("First", 10, 10)
    arcade.draw_text("Second", 10, 30)
    assert len(label_cache) == 2
    first, second = label_cache.values()
    assert first is not second
    assert first.text == "First"


def test_changing_text_without_frames_is_limited(window, label_cache, monkeypatch):
    """
    Without the event loop ticking the clock, every label looks in use, so
    changing text makes new labels, but the cache size still limits them
    """
    monkeypatch.setattr(text_module, "_DRAW_TEXT_CACHE_SIZE", 5)
    for i in range(20):
        arcade.draw_text(f"Count {i}", 10, 10)
    assert len(label_cache) == 5
    assert _label_for(label_cache, "Count 19").text == "Count 19"


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
