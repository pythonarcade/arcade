# Phase 1 Data Model: pyglet 3.0.dev6 Migration

**Feature**: [spec.md](./spec.md) | **Research**: [research.md](./research.md)

This migration has no persisted/business data model in the traditional sense.
The "entities" are runtime GPU/graphics objects and the classes that own them.
This document captures their shape, ownership, and lifecycle so the planning
and task-breakdown phases have a concrete structural reference.

## Entities

### Arcade Window Block UBO (new, Arcade-owned)

Replaces the current `self._window_block = window._matrices.ubo` reference
(`arcade/context.py:62`) with a UBO Arcade allocates and owns directly,
independent of pyglet's `Camera2D` ring buffer.

| Field | Type | Notes |
|---|---|---|
| `buffer` | `arcade.gl.Buffer` (or backend-native buffer) | Fixed-size GL buffer object, 128 bytes (two `Mat4`s: view + projection), allocated once per `ArcadeContext` |
| `binding_point` | `int` | Always `0` — matches existing Arcade shader `WindowBlock` layout; rebinding is done via raw `glBindBufferRange`, not through pyglet's `UniformBlock.set_binding()` (which forbids binding 0) |
| lifecycle | — | Created once in `ArcadeContext.__init__`; updated in place (no per-frame reallocation, no ring buffer, no growth) whenever view/projection change; destroyed with the context |

**Validation / invariants**:
- Buffer size never changes after creation (128 bytes fixed).
- No unbounded growth is possible by construction — there is exactly one
  buffer object, not a rotating pool (this is what makes SC-002 satisfiable
  by design rather than by careful call-count bookkeeping).
- Must be rebound at binding point 0 before every Arcade draw call that reads
  it (mirrors current `bind_window_block()` contract).

**Relationship to pyglet's own window-block UBO**: independent, coexisting
object. Arcade's UBO and pyglet's `Camera2D`-managed UBO are both valid
GL buffer objects; only one can be bound at GL binding point 0 at a given
draw call. See research.md §3 for the rebind-around-pyglet-native-draws risk
(e.g. `arcade.Text` → `pyglet.text.Label`).

### `ArcadeContext` (existing, modified)

`arcade/context.py`. Owns the Arcade Window Block UBO (above) instead of
borrowing pyglet's.

| Field | Change |
|---|---|
| `_window_block` | Was: reference to `window._matrices.ubo` (pyglet-owned). Now: reference to Arcade's own UBO object, created in `__init__`, never re-fetched from pyglet. |
| `_default_camera` | Unchanged type (`DefaultProjector`), but construction timing may move earlier relative to `Window.__init__` (see `Window` entity below). |
| `bind_window_block()` | Signature unchanged; implementation now binds Arcade's own buffer's `.id` instead of `self._window_block.buffer.id` sourced from pyglet. Backend-specific overrides in `arcade/gl/backends/opengl/context.py:436` and `arcade/gl/backends/webgl/context.py:384` both need the update. |
| `projection_matrix` / `view_matrix` (properties, `context.py:409-445`) | Getter/setter signatures unchanged. Setters currently write through `self.window.projection = value` / `self.window.view = value` (pyglet's own storage — the ring buffer in dev6, research.md §7). Must change to write directly into Arcade's own UBO instead, so Arcade's per-camera-update matrix writes never touch pyglet's ring buffer at all. |

### `Window` (existing, unmodified — `arcade/application.py`)

| Field | Change |
|---|---|
| `_ctx` | **No change.** research.md §4 originally predicted a construction-order `AttributeError` here; verified empirically against the actual pyglet `3.0.dev6` build and it does not occur — pyglet's own `_create_projection()` sets the private `self._default_camera` attribute directly during `__init__`, never invoking the public `default_camera` property Arcade overrides. `_ctx` continues to be constructed at `application.py:327`, unchanged. |
| `default_camera` (property, line 1085) | **No change.** `return self._ctx._default_camera` continues to work as-is; confirmed via the full camera/window test suite and via direct repeated `Window` construction. |

### pyglet `Camera2D` / `default_camera` (external, read-only dependency)

`pyglet/window/camera/camera2d.py`, `pyglet/window/__init__.py:1280-1342`.
Arcade does not modify this class. Arcade's `ArcadeContext`/`Window` code may
still *read* `window.projection` / `window.view` / `window.viewport` where it
needs pyglet's logical matrix values (e.g. to stay compatible with any
pyglet-native rendering path), but must not assume anything about where those
properties store their backing UBO, and must not drive pyglet's per-frame
ring-buffer lifecycle.

### Camera types (existing — `arcade/camera/`; corrected during implementation)

`OrthographicProjector`, `PerspectiveProjector`, `Camera2D` (Arcade's own,
distinct from pyglet's `Camera2D`), `DefaultProjector`. `DefaultProjector`
already went through `ArcadeContext.view_matrix` / `.projection_matrix`
(`arcade/context.py:409-445`), but implementation discovered that
`OrthographicProjector.use()` (`orthographic.py:132-133`),
`PerspectiveProjector.use()` (`perspective.py:168-169`), and Arcade's
`Camera2D.use()` (`camera_2d.py:299-300`) instead wrote through
`self._window.projection = ...` / `self._window.view = ...` — pyglet's own
properties, not Arcade's. Under `dev3` this was harmless (both paths wrote
into the same shared buffer); under `dev6` + Arcade's independently-owned UBO
(FR-005), these two paths are separate buffers, so cameras writing through
pyglet's properties never reached the UBO Arcade's shaders actually read,
producing stale/incorrect matrices. Fixed by changing all three call sites to
`self._window.ctx.projection_matrix = ...` / `self._window.ctx.view_matrix =
...`, matching `DefaultProjector`'s existing pattern. This is the concrete
mechanism behind FR-004 ("route matrix writes through a path compatible with
pyglet dev5+").

## State Transitions

```
ArcadeContext.__init__
  → allocate Arcade Window Block UBO (fixed 128 bytes)
  → bind_window_block()               # binds Arcade's buffer at GL binding 0
  → construct DefaultProjector (self._default_camera)

Window.__init__
  → super().__init__()                # pyglet init; sets self._default_camera
                                        # directly, never touches the public
                                        # default_camera property (research §4)
  → self._ctx = get_arcade_context(...)   # unchanged ordering; empirically safe

Per-frame draw
  → ArcadeContext.bind_window_block() re-affirms binding 0 = Arcade's UBO
  → (if delegating to pyglet-native draw, e.g. arcade.Text) verify/rebind as
    needed around that call (implementation-time verification, not a new
    public contract)
  → matrix writes update Arcade's UBO in place — no allocation, no growth
```

## Out of Scope for This Document

Byte-level UBO layout (std140 offsets for view/projection matrices) is
unchanged from the current 128-byte, two-`Mat4` layout already used by
Arcade's shaders (`bind_window_block`'s `128  # 32 x 32bit floats (two mat4)`)
— this migration does not change the shader-facing `WindowBlock` layout, only
who allocates and owns the buffer behind it.
