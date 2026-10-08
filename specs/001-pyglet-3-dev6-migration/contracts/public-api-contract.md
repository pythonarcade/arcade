# Public API Contract: pyglet 3.0.dev6 Migration

**Feature**: [spec.md](../spec.md) | **Data model**: [data-model.md](../data-model.md)

Arcade is a library, not a service — its "contract" is the public Python API
surface downstream game/tool developers depend on, plus the dependency
contract (the pyglet version pin). This document states what MUST stay stable
across this migration and what is explicitly allowed/expected to change.

## Dependency contract

| Before | After |
|---|---|
| `pyglet==3.0.dev3` (exact pin) | `pyglet==3.0.dev6` (exact pin) |
| No dual/range support | No dual/range support (unchanged policy) — FR-001 |

Consumers who pin their own `pyglet` version range spanning the `dev4`→`dev5`
break are not supported by this migration (Edge Case, spec.md); they must
follow Arcade's pin.

## Stable — MUST NOT change observable behavior

These are Arcade's existing public entry points. Their signatures and
observable behavior (given equivalent input) MUST be unchanged after this
migration:

- `arcade.Window.default_camera` (property) → still returns Arcade's
  `DefaultProjector` instance, unchanged (research.md §4: the predicted
  `AttributeError` root cause did not reproduce empirically, so no fix was
  needed here).
- `arcade.Window.ctx` → still returns the `ArcadeContext`.
- `ArcadeContext.view_matrix` / `.projection_matrix` / `.viewport` (properties
  at `arcade/context.py:409-445`) → same read/write semantics.
- `arcade.camera.Camera2D`, `OrthographicProjector`, `PerspectiveProjector`,
  `DefaultProjector` → same public constructors, `.use()` /
  `.activate()`-style methods, and produced view/projection matrices for
  equivalent inputs.
- `arcade.get_pixel()`, `arcade.get_image()` → unchanged.
- Rendered pixel output for existing camera/sprite/shape scenes → unchanged
  within the project's pixel-comparison tolerance (FR-006, SC-003).

## Removed — internal, not public API, safe to change

These are internals this migration necessarily touches; they were never part
of Arcade's supported public API, so changing them is not a breaking change:

- `ArcadeContext._window_block` — internal attribute, now Arcade-owned instead
  of borrowed from `window._matrices.ubo`.
- Any direct dependence (inside Arcade's own code) on `window._matrices` —
  removed entirely; this attribute no longer exists on pyglet's `Window` in
  `dev5`+.

## New behavioral guarantee introduced by this migration

- **Bounded UBO memory**: Arcade's window-block UBO is now a single
  fixed-size (128-byte) buffer allocated once per `ArcadeContext`, not a
  pyglet-managed ring buffer. This is a *new, stronger* guarantee
  (previously, behavior under `dev5`+ semantics was undefined/crashing) and
  is validated by SC-002 (100+ window/draw/reset cycles, zero
  "Growing UniformBufferObject" warnings).

## Documentation obligation (FR-008)

Because this migration changes which pyglet APIs Arcade depends on
internally (not Arcade's own public API), the only downstream-facing
documentation obligation is:
1. Bump the pinned `pyglet` version in the changelog (`CHANGELOG.md`).
2. Note, for advanced users who reach into pyglet directly alongside Arcade
   (e.g. mixing raw pyglet camera/window code with Arcade), that
   `window._matrices` no longer exists as of the pyglet version Arcade now
   requires, and that `window.default_camera` is now pyglet's own concept
   (a `pyglet.window.camera.camera2d.Camera2D`), distinct from
   `arcade.Window.default_camera` (Arcade's `DefaultProjector`) — both exist
   simultaneously and serve different roles.

## Verification harness contract (new, supports SC-003/FR-011)

A minimal reference-scene module is added under `tests/unit/rendering/`. Its
contract (revised after CI verification — see spec.md's Clarifications,
"CI verification results"):

- **Input**: a fixed, small set of representative render scenarios (sprite,
  shape, orthographic camera, perspective camera) — `scenes.py`.
- **Baseline**: PNG images captured once on the last known-good `dev3` build
  on real GPU hardware, checked into the repo (`generate_baseline.py`).
- **Automated check (runs everywhere — CI and local)**: structural sanity
  only — correct non-zero dimensions, not a single uniform/blank color, not
  fully black (`test_dev6_reference_images.py`). Pixel-tolerance comparison
  against the baseline was tried and dropped as the automated gate: CI's
  `xvfb` software rasterizer produces a consistent ~36% difference against
  hardware-captured baselines, confirmed unrelated to any actual rendering
  regression, so it isn't a reliable cross-rasterizer signal.
- **Manual check (local, real-GPU only)**: `image_compare.py`'s
  `compare_images()` remains available for a developer to run a precise
  per-pixel/percentage-difference comparison against the baseline by hand
  when investigating a suspected regression (reuses `arcade.get_image()`;
  no new third-party dependency).
- **Policy on a manually-observed mismatch** (FR-011): investigate first;
  only regenerate a baseline for a confirmed benign, pyglet-driven,
  documented difference; otherwise treat as a regression to fix in Arcade.
  A cross-rasterizer difference alone is not grounds for regenerating a
  baseline.
