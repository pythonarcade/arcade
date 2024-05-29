# The Rect, Part II
## The Rect-oning and the Vec-oning

- `Rect`
    - Added `Rect.distance_from_bounds()`
    - Added `point in rect` support for `Rect`
    - Added `*` and `/` support for scaling relative to `(0, 0)`.
    - Added bool() support (area is not 0)
    - Added support for round(), floor(), and ceil()
    - Added `.area` property
    - Functions expecting `Vec2` now accept `Tuple[AsFloat, AsFloat]`
    - Improved docstrings
    - Fixed `.viewport`
- Added type aliases `Point2` and `Point3`
- Camera
    - All camera functions now take `Point`, `Point2`, or `Point3` where points are expected
- Added `Rect` and it's constructors, `Vec2`, and `Vec3` to top-level module
- Added `Texture.draw_rect()`
- Added `BasicSprite.rect`
- Added `Section.rect`
- Added `SpriteSolidColor.from_rect()`
- Added `NinePatchTexture.from_rect()`
- Remove `IntRect`, `FloatRect`, `RectList`
- Rename the old `Rect` to `GUIRect`
