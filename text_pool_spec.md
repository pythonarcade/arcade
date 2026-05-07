# Arcade Enhancement: TextPool (Keyed Text Object Cache)

## Problem

Games that draw dynamic text every frame (scores, labels, status messages, player names) face a performance problem: creating `arcade.Text` objects is expensive because each construction resolves font names and creates a `pyglet.text.Label`. The existing `arcade.Text` docs acknowledge this — they recommend reusing Text instances rather than calling `draw_text()`.

But Arcade provides no built-in way to manage a pool of reusable Text objects. The result is that every game with dynamic text independently reinvents the same caching pattern.

## Real-World Evidence

The Worker Placement Game project (a board game using Arcade) has this identical `_text()` method copy-pasted across **5 separate classes**:

- `client/views/game_view.py` (~2900 lines, 40+ cached text keys)
- `client/ui/resource_bar.py`
- `client/ui/board_renderer.py` (via inline caching)
- `client/ui/tabbed_panel.py`
- `client/ui/game_log.py`

Each class maintains its own `_text_cache: dict[str, arcade.Text]` and implements the same method:

```python
def _text(self, key, text, x, y, color, font_size, **kwargs):
    if key in self._text_cache:
        t = self._text_cache[key]
        t.text = text
        t.x = x
        t.y = y
        t.color = color
        t.font_size = font_size
        return t
    t = arcade.Text(text, x, y, color, font_size=font_size, font_name="Tahoma", **kwargs)
    self._text_cache[key] = t
    return t
```

The pattern is always the same:
1. Look up by a string key (e.g., `"score_label"`, `"player_name_3"`)
2. If it exists, update its mutable properties (text, position, color, size)
3. If not, create it and store it
4. Call `.draw()` on the returned object

## Proposed API

A `TextPool` class in `arcade.text`:

```python
class TextPool:
    """A keyed cache of reusable Text objects.

    Avoids the cost of creating new Text objects every frame for
    dynamic text that changes position, content, or color frequently.

    Example::

        pool = arcade.TextPool(font_name="Arial")

        def on_draw(self):
            pool.draw("score", f"Score: {self.score}", 10, 580,
                       color=arcade.color.WHITE, font_size=16)
            pool.draw("fps", f"FPS: {arcade.get_fps():.0f}", 10, 560,
                       color=arcade.color.GRAY, font_size=12)
    """

    def __init__(self, font_name="calibri", **defaults):
        """Create a pool with shared default properties.

        Args:
            font_name: Default font for all text in this pool
            **defaults: Default kwargs passed to arcade.Text (e.g., bold, anchor_x)
        """
        ...

    def draw(self, key: str, text: str, x: float, y: float,
             color=arcade.color.WHITE, font_size: float = 12,
             **kwargs) -> arcade.Text:
        """Get or create a cached Text object, update it, and draw it.

        First call with a given key creates the Text object.
        Subsequent calls update the existing object's properties
        and draw it, avoiding reconstruction costs.

        Args:
            key: Unique identifier for this text slot
            text: The string to display
            x: X position
            y: Y position
            color: Text color
            font_size: Font size in points
            **kwargs: Additional properties (bold, anchor_x, anchor_y, etc.)

        Returns:
            The Text object (useful for measuring content_width, etc.)
        """
        ...

    def get(self, key: str, text: str, x: float, y: float,
            color=arcade.color.WHITE, font_size: float = 12,
            **kwargs) -> arcade.Text:
        """Like draw() but returns the Text without drawing it.

        Useful when you need to measure the text or draw it later.
        """
        ...

    def clear(self):
        """Remove all cached Text objects."""
        ...

    def remove(self, key: str):
        """Remove a specific cached Text object."""
        ...
```

## Design Decisions

### Why a separate class, not changes to `arcade.Text`?

`arcade.Text` is already well-designed for single instances. The pool pattern is about managing *collections* of text objects with keyed lookup. Making Text itself pooling-aware would complicate its API for users who only need one or two labels.

### Why string keys?

Games naturally name their text slots: `"score"`, `"player_name_3"`, `"round_label"`. This matches how every real-world implementation of this pattern works. Integer indices would be less readable and error-prone.

### Why `draw()` and `get()` as separate methods?

Sometimes you need the Text object to measure `content_width` before drawing (e.g., to position adjacent elements). `get()` returns the object without drawing; `draw()` is the common case that does both.

### Property update behavior

When an existing Text is retrieved, only the explicitly passed properties are updated. This allows properties set at creation (like `bold` or `anchor_x`) to persist without being re-specified every frame.

The `**defaults` in the constructor provide pool-wide defaults (like `font_name`) so individual `draw()` calls don't need to repeat them.

### Batch integration

The pool could optionally accept a `pyglet.graphics.Batch` and assign it to all created Text objects, enabling batch rendering:

```python
pool = arcade.TextPool(font_name="Arial", batch=my_batch)
# Individual draw() calls just update properties;
# my_batch.draw() renders everything at once
```

## Implementation Notes

- The core implementation is ~40 lines — the pattern is simple
- Should live in `arcade/text.py` alongside the existing `Text` class
- The `__init__` defaults should use the same font resolution as `Text` (call `_attempt_font_name_resolution` once, reuse for all pool members)
- Consider using `Text.__enter__`/`__exit__` context manager for efficient multi-property updates on existing objects (calls `pyglet.Label.begin_update()`/`end_update()`)

## Files to Change

| File | Change |
|------|--------|
| `arcade/text.py` | Add `TextPool` class |
| `arcade/__init__.py` | Export `TextPool` |
| `doc/` | Add example showing TextPool usage |
| `tests/unit/text/` | Unit tests for pool behavior |

## Test Plan

1. Create pool, draw text with key, verify it renders
2. Call draw() again with same key but different text — verify object is reused (same id)
3. Call draw() with different key — verify new object created
4. Verify `get()` returns object without drawing
5. Verify `clear()` removes all cached objects
6. Verify `remove()` removes specific key
7. Verify pool defaults (font_name) apply to all created text
8. Verify per-call kwargs override defaults
9. Verify `content_width` is accessible on returned objects
10. Performance test: 100 text objects, verify pool is faster than creating new Text each frame
