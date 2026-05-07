# Arcade Enhancement: Public Access to Child Layout Data

## Problem

When a widget is added to a layout (e.g., `UIAnchorLayout.add(child, anchor_x="left", align_x=50)`), the layout kwargs (`anchor_x`, `align_x`, `anchor_y`, `align_y`) are stored internally in a `_ChildEntry` named tuple, accessible only through the private `_children` list property.

The public `children` property strips this data:

```python
# arcade/gui/widgets/__init__.py line 529
@property
def children(self) -> list[UIWidget]:
    """Provides all child widgets."""
    return [child for child, data in self._children]
```

This means there's **no public way** to read or modify a child's layout parameters after it's been added, short of removing and re-adding it, or accessing the private `_children` attribute.

## Real-World Use Case

A game UI with buttons positioned in an `UIAnchorLayout`. On window resize, the button position (`align_x`, `align_y`) needs to update without rebuilding the entire widget tree:

```python
# Current workaround — accesses private API
entry = self._btn_anchor._children[0]  # _ChildEntry(child, data)
entry.data["align_x"] = new_x
entry.data["align_y"] = new_y
```

Without this, the only alternative is to call `remove()` + `add()` each frame, which is wasteful and causes flicker.

## Current Internal Structure

```python
# arcade/gui/widgets/__init__.py

class _ChildEntry(NamedTuple):
    child: UIWidget
    data: dict

class UIWidget:
    _children = ListProperty[_ChildEntry]()

    def add(self, child, **kwargs):
        child.parent = self
        self._children.append(_ChildEntry(child, kwargs))
        return child

    def remove(self, child):
        child.parent = None
        for c in self._children:
            if c.child == child:
                self._children.remove(c)
                return c.data  # Note: remove() already returns the data
        return None

    @property
    def children(self) -> list[UIWidget]:
        return [child for child, data in self._children]
```

Note that `remove()` already returns the layout data dict, which suggests the framework considers this data useful — it just doesn't provide a way to access it without removing the child.

## Proposed API

Add two methods to `UIWidget`:

```python
def get_child_data(self, child: UIWidget) -> dict | None:
    """Get the layout data for a child widget.

    Returns the kwargs dict that was passed when the child was added
    (e.g., anchor_x, align_x for UIAnchorLayout children).
    Modifying the returned dict will affect the child's layout
    on the next do_layout() call.

    Args:
        child: The child widget to look up.

    Returns:
        The layout data dict, or None if the child is not found.
    """
    for entry in self._children:
        if entry.child == child:
            return entry.data
    return None

def get_child_entry(self, index: int) -> tuple[UIWidget, dict]:
    """Get the child widget and its layout data by index.

    Args:
        index: The index of the child (0-based, in add order).

    Returns:
        A tuple of (child_widget, layout_data_dict).

    Raises:
        IndexError: If the index is out of range.
    """
    entry = self._children[index]
    return entry.child, entry.data
```

### Usage After Change

```python
# Look up by child reference
data = layout.get_child_data(my_button_row)
if data:
    data["align_x"] = new_x
    data["align_y"] = new_y

# Look up by index
child, data = layout.get_child_entry(0)
data["align_x"] = new_x
```

## Design Decisions

### Why return a mutable dict?

The layout data dict is already mutable internally — `do_layout()` reads from it each time. Returning it directly lets callers modify positioning without remove/re-add cycles, which is the primary use case. This matches the existing pattern where `remove()` returns the same dict.

### Why two methods?

- `get_child_data(child)` — when you have a reference to the child widget (common case)
- `get_child_entry(index)` — when you know the position but not the widget (useful for single-child layouts)

### Why not make `_ChildEntry` public?

`_ChildEntry` is a `NamedTuple` with `child` and `data` fields. Making it public is an option, but the proposed methods are simpler — callers don't need to learn about a new type. The internal storage structure can evolve independently.

### Why not a `children_with_data` property?

A property returning `list[tuple[UIWidget, dict]]` would work but encourages iterating the full list. The lookup methods are more intentional and match the typical use case of updating a specific child.

## Files to Change

| File | Change |
|------|--------|
| `arcade/gui/widgets/__init__.py` | Add `get_child_data()` and `get_child_entry()` to `UIWidget` |
| `tests/unit/gui/` | Tests for both methods |
| `doc/` | Document the new methods, add example |

## Test Plan

1. `get_child_data(child)` returns the correct dict for an added child
2. `get_child_data(unknown_widget)` returns `None`
3. Modifying the returned dict affects layout on next `do_layout()` call
4. `get_child_entry(0)` returns first child and its data
5. `get_child_entry(-1)` returns last child (Python index semantics)
6. `get_child_entry(out_of_range)` raises `IndexError`
7. Works with `UIAnchorLayout`, `UIBoxLayout`, `UIGridLayout`
8. Returned dict matches what was passed to `add()`
9. After `remove()` + `add()`, `get_child_data()` returns the new data
