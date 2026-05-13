import pytest
import arcade


def test_draw_creates_and_returns_text(window):
    """draw() should create a Text object and return it."""
    pool = arcade.TextPool()
    result = pool.draw("score", "Score: 0", 10, 580)
    assert isinstance(result, arcade.Text)
    assert result.text == "Score: 0"
    assert result.x == 10
    assert result.y == 580


def test_same_key_reuses_object(window):
    """Calling draw() twice with the same key should return the same Text instance."""
    pool = arcade.TextPool()
    first = pool.draw("label", "Hello", 10, 10)
    second = pool.draw("label", "World", 20, 20)
    assert first is second
    assert second.text == "World"
    assert second.x == 20
    assert second.y == 20


def test_different_keys_create_different_objects(window):
    """Different keys should produce distinct Text instances."""
    pool = arcade.TextPool()
    text_a = pool.draw("a", "Alpha", 0, 0)
    text_b = pool.draw("b", "Beta", 10, 10)
    assert text_a is not text_b


def test_get_returns_without_drawing(window):
    """get() should return a Text object without calling draw."""
    pool = arcade.TextPool()
    result = pool.get("info", "Test", 5, 5)
    assert isinstance(result, arcade.Text)
    assert result.text == "Test"


def test_get_reuses_object(window):
    """get() should reuse the same cached object on subsequent calls."""
    pool = arcade.TextPool()
    first = pool.get("info", "A", 0, 0)
    second = pool.get("info", "B", 1, 1)
    assert first is second
    assert second.text == "B"


def test_clear_removes_all(window):
    """clear() should remove all cached Text objects."""
    pool = arcade.TextPool()
    pool.get("a", "A", 0, 0)
    pool.get("b", "B", 0, 0)
    pool.clear()

    new_a = pool.get("a", "A2", 5, 5)
    assert new_a.text == "A2"
    assert new_a.x == 5


def test_remove_specific_key(window):
    """remove() should delete only the specified key."""
    pool = arcade.TextPool()
    original = pool.get("target", "X", 0, 0)
    pool.get("keep", "Y", 0, 0)

    pool.remove("target")

    recreated = pool.get("target", "X2", 10, 10)
    assert recreated is not original

    kept = pool.get("keep", "Y", 0, 0)
    assert kept.text == "Y"


def test_remove_missing_key_raises(window):
    """remove() should raise KeyError for a missing key."""
    pool = arcade.TextPool()
    with pytest.raises(KeyError):
        pool.remove("nonexistent")


def test_pool_defaults_apply(window):
    """Constructor defaults should be passed through to created Text objects."""
    pool = arcade.TextPool(font_name="arial", bold=True, anchor_x="center")
    result = pool.get("label", "Hello", 0, 0)
    assert result.bold is True
    assert result.anchor_x == "center"


def test_per_call_kwargs_override_defaults(window):
    """Per-call kwargs should override constructor defaults."""
    pool = arcade.TextPool(anchor_x="left")
    result = pool.get("label", "Hello", 0, 0, anchor_x="right")
    assert result.anchor_x == "right"


def test_properties_update_on_reuse(window):
    """All standard properties should update when reusing a cached object."""
    pool = arcade.TextPool()
    pool.get("item", "Old", 0, 0, color=arcade.color.WHITE, font_size=12)
    updated = pool.get(
        "item", "New", 100, 200,
        color=arcade.color.RED, font_size=24,
    )
    assert updated.text == "New"
    assert updated.x == 100
    assert updated.y == 200
    assert updated.color == arcade.color.RED
    assert updated.font_size == 24


def test_content_width_accessible(window):
    """content_width should be readable on returned Text objects."""
    pool = arcade.TextPool()
    result = pool.get("measure", "Hello World", 0, 0, font_size=16)
    assert isinstance(result.content_width, (int, float))
    assert result.content_width > 0
