# Arcade Enhancement: Interactive Sprite Widget

## Problem

Arcade has two parallel input systems for handling mouse clicks:

1. **UI system** (`UIManager` / `UIWidget` / `UIInteractiveWidget`) — full event dispatch with hover, press, click states, focus management, and callback registration
2. **Sprite system** (`Sprite` / `SpriteList` / `get_sprites_at_point()`) — spatial queries that return which sprites are under a point, but no event dispatch

Games that use sprites as clickable elements (card selection dialogs, board spaces, inventory grids) must bridge these two systems manually. Arcade provides no built-in way to make a Sprite respond to UI input events.

### What exists today

`UISpriteWidget` (`arcade/gui/widgets/__init__.py` line 952) wraps a `Sprite` for **display only** — it renders the sprite into the UI tree but inherits from `UIWidget`, not `UIInteractiveWidget`, so it has no click/hover handling.

`UITextureButton` (`arcade/gui/widgets/buttons.py` line 30) accepts textures and responds to clicks, but it's a full styled widget with text overlay support — it doesn't wrap an existing `Sprite` or integrate with a `SpriteList`.

Neither helps the common case: "I have sprites on screen, I want to know when the user clicks one."

## Real-World Evidence

The Worker Placement Game project has this pattern in multiple places:

### Pattern 1: Card Selection Dialog (`client/ui/dialogs.py`)

A dialog displays card sprites and detects which one was clicked:

```python
class CardSpriteSelectionDialog:
    def __init__(self, ...):
        self._sprite_list = arcade.SpriteList()
        self._card_ids: list[str] = []

    def _rebuild_sprites(self):
        self._sprite_list.clear()
        for card in self.cards:
            sprite = arcade.Sprite(card_image_path)
            sprite.scale = target_width / sprite.texture.width
            sprite.position = (cx, cy)
            self._sprite_list.append(sprite)
            self._card_ids.append(card["id"])

    def draw(self):
        self._sprite_list.draw()

    def on_click(self, x, y) -> bool:
        hits = arcade.get_sprites_at_point((x, y), self._sprite_list)
        if hits:
            idx = self._sprite_list.index(hits[0])
            card_id = self._card_ids[idx]
            self.on_select(card_id)
            return True
        return False
```

### Pattern 2: Board Space Hit Testing (`client/ui/board_renderer.py`)

The board tracks clickable rectangles for sprites and resolves clicks manually:

```python
class BoardRenderer:
    def __init__(self):
        self._space_rects: dict[str, tuple] = {}

    def draw(self):
        # After drawing each sprite, register its rect
        self._space_rects[f"quest_card_{qid}"] = (x, y, w, h)
        self._space_rects[f"building_card_{bid}"] = (x, y, w, h)

    def get_space_at(self, x, y) -> str | None:
        for space_id, (rx, ry, rw, rh) in self._space_rects.items():
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                return space_id
        return None
```

### Pattern 3: Game View Click Dispatch (`client/views/game_view.py`)

The main view manually routes mouse events through a priority chain:

```python
def on_mouse_press(self, x, y, button, modifiers):
    # 1. Check dialog sprites
    if self._card_sprite_dialog:
        if self._card_sprite_dialog.on_click(x, y):
            return
    # 2. Check board sprites
    space_id = self.board_renderer.get_space_at(x, y)
    if space_id:
        self._handle_space_click(space_id)
```

No hover effects are implemented because managing hover state across sprites requires even more manual tracking (`on_mouse_motion` → `get_sprites_at_point()` → track previous hover → update visual state).

## Analysis of the Gap

The gap is specifically between `UISpriteWidget` (display-only) and `UIInteractiveWidget` (full interaction). Making a sprite interactive requires:

1. **Hit testing** — already solved by `get_sprites_at_point()` but not connected to the UI event system
2. **State tracking** — `UIInteractiveWidget` tracks `hovered`, `pressed`, `disabled` states; sprite users must reimplement this
3. **Event dispatch** — `UIInteractiveWidget` fires `on_click` events with proper button/modifier data; sprite users get raw coordinates only
4. **Visual feedback** — `UIInteractiveWidget` updates rendering based on state (hover texture, pressed texture); sprite users must manage this manually

## Proposed API

Extend `UISpriteWidget` to support interaction by adding a new class:

```python
class UIInteractiveSpriteWidget(UISpriteWidget, UIInteractiveWidget):
    """A sprite embedded in the UI tree that responds to click and hover events.

    Wraps an existing Sprite, rendering it as a UI widget with full
    interactive behavior: hover detection, press tracking, click events,
    and optional visual state changes.

    Example::

        sprite = arcade.Sprite("card.png")
        widget = UIInteractiveSpriteWidget(sprite=sprite)

        @widget.event("on_click")
        def on_click(event):
            print(f"Card clicked at {event.x}, {event.y}")

        ui_manager.add(widget)

    For hover feedback, override do_render or listen for property changes::

        widget.bind(hovered=lambda prop: update_outline(widget))
    """

    def __init__(
        self,
        *,
        sprite: Sprite,
        width: float | None = None,
        height: float | None = None,
        **kwargs,
    ):
        """Create an interactive sprite widget.

        Args:
            sprite: The sprite to display and make interactive.
            width: Widget width. Defaults to sprite texture width.
            height: Widget height. Defaults to sprite texture height.
            **kwargs: Additional UIWidget kwargs (size_hint, etc.)
        """
        ...
```

### Usage

```python
# Single clickable sprite
card_sprite = arcade.Sprite("quest_card.png")
card_widget = arcade.gui.UIInteractiveSpriteWidget(sprite=card_sprite)

@card_widget.event("on_click")
def on_click(event):
    print("Card selected!")

# Or with direct callback assignment
card_widget.on_click = lambda event: select_card(card_id)

# Add to UI tree (gets full event dispatch automatically)
ui_manager.add(card_widget)

# Place in a layout
layout = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
for card in hand:
    sprite = arcade.Sprite(card.image_path)
    widget = arcade.gui.UIInteractiveSpriteWidget(sprite=sprite)
    widget.on_click = lambda e, c=card: play_card(c)
    layout.add(widget)
```

### Hover Feedback

Since `UIInteractiveWidget` already tracks `hovered` and `pressed` states via observable properties, visual feedback comes naturally:

```python
widget = UIInteractiveSpriteWidget(sprite=my_sprite)

# React to hover state changes
def on_hover_change(prop):
    if widget.hovered:
        widget.sprite.color = (220, 220, 255)  # Tint on hover
    else:
        widget.sprite.color = (255, 255, 255)  # Normal

widget.bind(hovered=on_hover_change)
```

## Design Decisions

### Why extend `UISpriteWidget` rather than creating something new?

`UISpriteWidget` already handles sprite rendering within the UI tree — it calls `sprite.update()`, `sprite.update_animation()`, and draws the sprite to the widget surface. The only thing missing is interaction. Combining it with `UIInteractiveWidget` via multiple inheritance follows the existing pattern: `UITextureButton` does the same thing with `UIInteractiveWidget` + `UIStyledWidget` + `UITextWidget`.

### Why not add click handling directly to `UISpriteWidget`?

Keeping `UISpriteWidget` as a non-interactive display widget preserves the existing distinction between display widgets (`UIWidget` subclasses) and interactive widgets (`UIInteractiveWidget` subclasses). Some uses of `UISpriteWidget` are purely decorative — forcing interaction handling on all of them would be unnecessary overhead and a breaking change.

### Why not make Sprites themselves UI-aware?

Sprites live in the game world coordinate system; UI widgets live in the UI coordinate system with their own camera. Mixing these concepts in the `Sprite` class itself would conflate two different concerns. The widget wrapper is the right boundary — it translates between the two systems.

### Why not a clickable SpriteList?

A `SpriteList` that dispatches click events per-sprite would be useful but is a larger change. It would require integrating `SpriteList` with the `UIManager` event system, which currently only walks the widget tree. The single-sprite widget is a smaller, composable building block — multiple clickable sprites can be placed in a `UIBoxLayout` or `UIGridLayout` to achieve the same effect.

### What about the `on_click` vs `on_select` naming?

The existing UI system uses `on_click` for single-widget click events. This is consistent. A hypothetical future `UIClickableSpriteList` could use `on_select(sprite, index)` for multi-sprite selection, but that's a separate concern.

### MRO (Method Resolution Order)

With `UIInteractiveSpriteWidget(UISpriteWidget, UIInteractiveWidget)`:
- `UISpriteWidget` inherits from `UIWidget`
- `UIInteractiveWidget` inherits from `UIWidget`
- Python's MRO resolves this cleanly via C3 linearization
- `on_event` from `UIInteractiveWidget` handles input; `do_render` from `UISpriteWidget` handles drawing
- This matches how `UITextureButton(UIInteractiveWidget, UIStyledWidget, UITextWidget)` works

## Files to Change

| File | Change |
|------|--------|
| `arcade/gui/widgets/__init__.py` | Add `UIInteractiveSpriteWidget` class after `UISpriteWidget` |
| `arcade/gui/__init__.py` | Export `UIInteractiveSpriteWidget` |
| `tests/unit/gui/` | Tests for click, hover, press states, callback dispatch |
| `doc/` | Document the new widget, add interactive sprite example |

## Test Plan

1. Click on the sprite fires `on_click` event with correct coordinates
2. Click outside the sprite does not fire `on_click`
3. `hovered` property updates on mouse enter/leave
4. `pressed` property is `True` between mouse press and release
5. Click with `disabled=True` does not fire `on_click`
6. Sprite animation continues to update (`update_animation` called)
7. Widget works inside `UIBoxLayout` and `UIAnchorLayout`
8. Multiple `UIInteractiveSpriteWidget` instances — only the topmost receives the click
9. Callback registration works via `@widget.event("on_click")` decorator
10. Callback registration works via `widget.on_click = callback` assignment
11. `hovered` state can be bound to visual changes via `widget.bind()`
12. Widget rect matches sprite dimensions when no explicit width/height given
