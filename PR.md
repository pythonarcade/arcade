# The Rect, Part II
## The Rect-oning and the Vec-oning

- Added type aliases `Point2` and `Point3`
- `Rect`
    - Added `Rect.distance_from_bounds()`
    - Added `point in rect` support for `Rect`
    - Functions expecting `Vec2` now accept `Tuple[AsFloat, AsFloat]`
    - Improved docstrings
- Added `Rect` and it's constructors, `Vec2`, and `Vec3` to top-level module
- Added `Texture.draw_rect()`
- Added `BasicSprite.rect`
- Remove `IntRect`, `FloatRect`, `RectList`
- Rename the old `Rect` to `GUIRect`
