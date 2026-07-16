# Phase 0 Research: pyglet 3.0.dev6 Migration

**Feature**: [spec.md](./spec.md) | **Date**: 2026-07-16

This research was performed against the actual pyglet `3.0.dev6` source available
locally at `C:\Users\PaCra\Projects\pyglet` (git tag `v3.0.dev6`, confirmed via
`pyglet/__init__.py: version = '3.0.dev6'`), not just the bump report's summary.

## 1. Where does the window matrix UBO live now?

**Decision**: Arcade must stop reading `window._matrices.ubo` (removed) and
instead treat `window.default_camera` (a lazily-created
`pyglet.window.camera.camera2d.Camera2D`, `pyglet/window/camera/camera2d.py:125`)
as the sole owner of pyglet's window-block UBO. `Window.projection` / `.view` /
`.viewport` (`pyglet/window/__init__.py:1294-1342`) are now thin properties that
delegate to `self.default_camera.projection` / `.view_matrix` / `.viewport`.

**Rationale**: This is a direct, verified fact of the dev6 source (not
inferred) — see the exact property bodies:

```python
# pyglet/window/__init__.py:1294
@property
def projection(self) -> Mat4:
    return self.default_camera.projection

@projection.setter
def projection(self, matrix: Mat4) -> None:
    self.default_camera.projection = matrix
```

`Window.default_camera` itself is a read-only property (not a plain instance
attribute) that lazily constructs a `Camera2D` on first access and caches it as
`self._default_camera` (`pyglet/window/__init__.py:1280-1292`).

**Alternatives considered**: Continuing to poke a private pyglet attribute
(e.g. `window.default_camera._window_block` or similar) was rejected — it
depends on pyglet internals that are more likely to change again than the
public `default_camera` property, and does not address the ring-buffer growth
problem (see §2).

## 2. Why does a naive bump cause unbounded UBO growth?

**Decision**: Treat this as an architectural mismatch, not a bug to patch —
confirms the spec's existing FR-005 direction (Arcade fully owns its own UBO).

**Rationale**: pyglet's `RingBuffer` / `UniformBufferObject`
(`pyglet/graphics/buffer.py:161`, `:302`) pre-reserves a fixed number of
`BufferRange`s per resource (`copies_per_resource`, default 3 on `Camera2D`)
representing "frames in flight." Release only happens via
`FrameResourceManager.frame_begin()` → `_release_slot()`
(`pyglet/graphics/api/base.py:238-296`), which decrements a
`frame_use_count` as pyglet's own frame-slot rotation comes back around —
**there is no manual free/release API**. If a consumer calls `commit()` /
mutates the UBO more times per frame than there are reserved ranges (which is
exactly what happens when Arcade drives its own render loop and calls into
matrix-setting logic without participating in pyglet's per-frame slot
rotation), `acquire_writable_slice_from_ranges` hits its "wrapped while full"
branch and **permanently appends a new `BufferRange`**
(`pyglet/graphics/buffer.py:229-271`), doubling the backing GL buffer via
`_ensure_storage_for_commit(..., force_double=True)`
(`buffer.py:416-457`). This list of ranges never shrinks. This is the literal
mechanism behind the "Growing UniformBufferObject" warning referenced in
SC-002.

**Alternatives considered**:
- *Drive pyglet's per-frame lifecycle explicitly (call `frame_begin`/whatever
  hooks pyglet expects each frame)* — rejected per the spec's existing
  clarification: Arcade owns its own render loop and does not want a hard
  dependency on pyglet's internal frame-resource bookkeeping, which is not a
  stable/public contract.
- *Set `strict=True` to fail fast instead of growing* — does not solve the
  crash, only changes it from a silent memory leak to an immediate
  `RuntimeError`; still requires Arcade to stop over-subscribing pyglet's ring
  buffer.

## 3. Can Arcade register its own UBO at GL binding point 0 alongside pyglet's?

**Decision**: No — binding point 0 is hard-reserved by pyglet for its own
`WindowBlock`, enforced at the `UniformBlock.set_binding()` level
(`pyglet/graphics/shader.py:1005`: `assert binding != 0, "Binding 0 is
reserved for the internal Pyglet 'WindowBlock'."`) and documented in
`doc/programming_guide/rendering.rst:196`. However, Arcade does **not** go
through that pyglet API today — `OpenGLArcadeContext.bind_window_block()`
(`arcade/gl/backends/opengl/context.py:436-443`) issues a raw
`gl.glBindBufferRange(GL_UNIFORM_BUFFER, 0, self._window_block.buffer.id, 0,
128)` directly against the GL binding point, bypassing pyglet's shader
introspection layer entirely. This means Arcade can continue to rebind GL
binding point 0 to a buffer object it fully owns, as long as it is careful
about *when* it does so relative to any pyglet-native draw call that expects
pyglet's own `WindowBlock` contents to be bound there (see Risk below).

**Rationale**: Confirms FR-005's "fully owning its own matrix UBO" direction
is technically viable without any pyglet API change or cooperation — Arcade
already has an existing, working mechanism (a raw GL bind call) that pyglet's
binding-0 restriction does not block.

**Alternatives considered**: Using a non-zero binding point for Arcade's own
UBO and updating all of Arcade's shaders' `layout(binding=N)` declarations —
rejected as unnecessarily invasive (touches every Arcade shader) when the
existing binding-0 raw-bind approach still works.

**Note on the "offscreen/headless rendering" edge case (spec.md Edge Cases)**:
this design answers it by construction, not by special-casing. Arcade's own
UBO (§7, data-model.md) is a plain GL buffer object created and updated by
`ArcadeContext` directly — it has no dependency on a visible window surface,
on pyglet's frame-presentation cycle, or on `default_camera`'s ring buffer at
all. Whatever context Arcade is running under (windowed or Arcade's existing
headless mode), the same buffer-allocation and bind logic applies unchanged.
No dedicated headless test task is added for this migration; the existing
headless-mode test coverage already exercises the code paths this migration
touches (`ArcadeContext.__init__`, `bind_window_block`, matrix setters).

**Risk flagged for planning/implementation (not spec-blocking)**: Arcade's
own text objects (`arcade.Text`) delegate to `pyglet.text.Label`, which draws
through pyglet's normal batch/shader path and expects GL binding point 0 to
hold *pyglet's* `Camera2D`-managed UBO at draw time. If Arcade leaves its own
private UBO bound at binding 0 when a pyglet-native draw call executes (e.g.
inside `arcade.Text.draw()`), pyglet's text will render with Arcade's matrices
instead of its own — likely harmless when the two are numerically identical
(same viewport/projection), but not guaranteed if they ever diverge (e.g.
scissored/sub-viewport rendering). Implementation should verify text
rendering visually after the migration and, if needed, rebind pyglet's own
window-block UBO immediately before delegating to any pyglet-native draw path
and restore Arcade's own binding immediately after.

## 4. `default_camera` name collision / `AttributeError` — predicted but did not reproduce

**Original decision (pre-implementation)**: Based on static reading of
`arcade/application.py:1085` (Arcade's `default_camera` property returning
`self._ctx._default_camera`) and pyglet's inherited `projection`/`view`/
`viewport` properties calling `self.default_camera`
(`pyglet/window/__init__.py:1294-1342`), this section originally predicted
that pyglet-internal code during `Window.__init__` would trigger Arcade's
overridden `default_camera` property before `self._ctx` exists
(constructed at `arcade/application.py:327`, after `super().__init__()`),
raising `AttributeError: 'Window' object has no attribute '_ctx'`.

**Empirical correction (during implementation/T006)**: This was verified
directly against the actual installed pyglet `3.0.dev6`
(`.venv/Lib/site-packages/pyglet/window/__init__.py:578-581`) and does
**not** reproduce. `_create_projection()` — called during pyglet's
`Window.__init__` — assigns the **private** instance attribute
`self._default_camera` directly:

```python
# pyglet/window/__init__.py:578-579
def _create_projection(self) -> None:
    self._default_camera = self._create_default_camera()
```

This never invokes the **public** `default_camera` property (the one
Arcade's `Window` subclass overrides), so there is no MRO collision during
`__init__` after all — pyglet's own internal code paths never call
`self.default_camera`, `self.projection`, `self.view`, or `self.viewport`
during construction; they only ever touch the private attribute.

Confirmed two ways:
1. The full `tests/unit/camera` + `tests/unit/window` suite (125 tests)
   passes with no `AttributeError` after the FR-005 UBO-ownership fix (§1-3,
   §7) was applied, with no `Window.__init__` reordering.
2. Directly creating and closing three fresh `arcade.Window` instances in
   sequence in an interactive script raised no `AttributeError` in any
   iteration.

**Outcome**: No code change was needed for this predicted failure mode.
FR-003's acceptance scenario ("window/context construction does not raise
`AttributeError`") is satisfied without modification — the actual root cause
of the migration's crash was entirely the UBO-ownership issue (§1-3, §7),
not a `default_camera` MRO collision. This is retained in this document as a
record that the prediction was investigated and disproven, not deleted,
since a plausible-sounding static-analysis conclusion turned out to need
runtime verification.

## 5. Existing test/verification infrastructure

**Decision**: SC-003's "existing image-comparison tolerance" language in the
spec describes an infrastructure that does not currently exist in this
repository as a distinct pixel-diff/golden-image harness (no `pytest-mpl`, no
checked-in baseline PNGs, no `compare_image` helper were found anywhere under
`tests/` or `pyproject.toml`). What does exist:
- `tests/unit/camera/`: `test_camera2d.py`, `test_orthographic_projector.py`,
  `test_perspective_projector.py`, `test_viewport_projector.py`,
  `test_camera_controller_methods.py`, `test_camera_shake.py`.
- `tests/unit/window/`: `test_fullscreen.py`, `test_view.py`, `test_window.py`.
- `tests/unit/test_screenshot.py`: reads individual pixels/framebuffers via
  `arcade.get_pixel()` / `arcade.get_image()` — a usable primitive for
  building comparisons, but not itself a comparison harness.
- `tests/integration/examples/test_examples.py` and
  `tests/integration/tutorials/test_tutorials.py`: run example/tutorial
  scripts sequentially in one process — this is the realistic reproduction of
  the "multiple windows created/destroyed in one process" scenario that
  triggers unbounded UBO growth today (Edge Case 1).
- `tests/conftest.py`: creates one real `arcade.Window` for the whole test
  session (`ARCADE_TEST=True`), supports `--gl-backend` for opengl/webgl.

**Rationale**: Since no reference-image harness exists, SC-003 needs a
minimal, narrowly-scoped one built as part of this migration rather than
assuming pre-existing infrastructure. Given `get_image()` already exists,
the lightest-weight approach is a small dedicated test module that renders a
handful of representative scenes (sprite, shape, orthographic camera,
perspective camera), captures PNGs via `get_image()`, and diffs them against
checked-in baseline PNGs (captured once, pre-migration, on the still-working
`dev3` code) using a simple per-pixel/percentage-difference threshold — no new
third-party dependency required (PIL is already a dependency via `context.py`
imports).

**Alternatives considered**: Adopting `pytest-mpl` or a similar third-party
image-comparison framework — rejected as disproportionate scope for a
migration whose real acceptance bar is "no visible rendering regression," not
general-purpose visual regression tooling; a small in-repo harness meets
FR-011/SC-003 without adding new dependencies or maintenance surface.

## 6. Toolchain / environment facts (no ambiguity, recorded for Technical Context)

- Python: `>=3.10`, CI matrix tests 3.10–3.14 (`pyproject.toml`,
  `.github/workflows/test.yml`).
- Current pin: `pyglet==3.0.dev3` (`pyproject.toml:25`, `uv.lock`).
- Dependency/sync tool: `uv` (`uv sync --no-group docs`, `uv run pytest`).
- CI: GitHub Actions, `ubuntu-latest` + `xvfb-run` (headless software
  rendering), unchanged by this migration (per clarification session
  2026-07-16, environment correction) — runs alongside, not instead of, local
  Windows verification.
- No "bump report" document exists inside this repository; the document
  referenced by the spec's Overview is external to this checkout. This
  research treats the actual pyglet dev6 source (found at
  `C:\Users\PaCra\Projects\pyglet`) as the authoritative technical reference
  where it's available, and the spec's Assumptions section as the
  authoritative source for anything not independently verifiable here.

## 7. How does Arcade currently write matrices, and why does that matter for the fix?

**Decision**: The fix must change `ArcadeContext.projection_matrix` /
`view_matrix` setters themselves, not just `bind_window_block()`.

**Rationale**: `ArcadeContext.projection_matrix.setter` and `.view_matrix.setter`
(`arcade/context.py:421-445`) currently delegate directly to
`self.window.projection = value` / `self.window.view = value` — i.e. every
Arcade matrix update already flows through pyglet's own window-matrix
storage. In `dev3`, `window.projection`/`window.view` write into the single
shared buffer that `ArcadeContext._window_block` also points at
(`window._matrices.ubo`), so this was harmless — reader and writer were the
same physical buffer. In `dev6`, `window.projection`/`window.view` write
into `Camera2D`'s ring-buffer-backed UBO (`camera2d.py:169-193` calls
`_apply_changed_cpu_data`, which commits into the ring buffer) — meaning
**every** Arcade matrix update is itself a ring-buffer commit, and Arcade
updates matrices far more often per frame than pyglet's `copies_per_resource`
(3) frames-in-flight slots can absorb without participating in pyglet's own
frame-slot rotation. This is the second, more precise half of the growth
mechanism described in §2: it isn't just "Arcade doesn't drive the frame
lifecycle," it's "Arcade's existing setters actively write into pyglet's ring
buffer on every camera update."

**Consequence for the fix**: Per FR-005/data-model.md, Arcade's
`projection_matrix`/`view_matrix` setters must stop writing through
`self.window.projection`/`self.window.view` and instead write directly into
Arcade's own fixed-size UBO. Reads (the getters) may still read
`self.window.projection`/`self.window.view` if Arcade wants to stay
informed of pyglet's own logical camera state for interop purposes, but the
authoritative value backing Arcade's rendering must come from Arcade's own
buffer, updated by Arcade's own setter logic. This does not change the public
property signatures (`contracts/public-api-contract.md`), only their
internal implementation.

**Alternatives considered**: Keep writing through
`self.window.projection`/`.view` but throttle/coalesce calls to stay under
`copies_per_resource` — rejected as fragile (depends on an internal pyglet
constant and on Arcade correctly participating in frame boundaries it
doesn't otherwise track) compared to simply not depending on pyglet's ring
buffer for Arcade's own rendering path at all.

## 8. The real `default_camera` collision: pyglet's own batch-draw fallback, not `Window.__init__`

**Decision**: §4's predicted `AttributeError` during `Window.__init__` didn't
reproduce, but a *different*, very real manifestation of the same underlying
MRO collision does: pyglet's own `Batch.draw()` (used internally by
`pyglet.text.Label.draw()`, which `arcade.Text`/`arcade.draw_text()`
delegate to) falls back to `ctx.window.default_camera` whenever no explicit
camera is supplied to a draw call. Since Arcade's `Window.default_camera`
override — being the most-derived definition — intercepts *every* access to
that name, pyglet's own fallback gets Arcade's `DefaultProjector` instead of
its own `Camera2D`, and then calls methods/attributes on it that only a real
pyglet camera implements: `.view.scissor`, `.begin(draw_context=..., commit=...)`,
`.get_group_scissor_area()`. `DefaultProjector` had none of these, so any
pyglet-native text draw crashed with `AttributeError: 'DefaultProjector'
object has no attribute 'view'` (found via `tests/integration/examples/test_examples.py`
running the `platform_tutorial` examples, which draw score text every frame).

Separately, pyglet's *own* `Window.projection`/`.view` base-class properties
(unrelated to the batch-draw path) delegate to `self.default_camera.projection`
/ `.view_matrix` (research.md §1) — for the same MRO reason, any code that
reads/writes `window.projection`/`window.view` (pyglet's own internals, test
infrastructure such as `tests/conftest.py`'s `WindowProxy`, or downstream
user code) hits `DefaultProjector`, which didn't expose `.projection` or
`.view_matrix` either, crashing with `AttributeError: 'DefaultProjector'
object has no attribute 'projection'` (found via
`arcade/examples/gl/chip8_display.py`, which reads `window.projection` to
feed a shader uniform).

**Rationale for the fix**: Arcade's public contract requires
`Window.default_camera` to keep returning a `DefaultProjector`
(`contracts/public-api-contract.md`) — that cannot change. The alternative of
reimplementing pyglet's full internal camera/view-hierarchy protocol
(child views, transform stacks, group-scoped scissor resolution) on
`DefaultProjector` was rejected as exactly the kind of deep coupling to
pyglet's internal, changeable implementation this migration is trying to
get *away* from (see FR-005's rationale). Instead, `DefaultProjector` gained
a minimal duck-typing compatibility shim (`arcade/camera/default.py`):
- `.view` → returns `self` (so `.view.scissor` resolves to its own `.scissor`,
  normally `None`).
- `.begin(*, draw_context, commit=True)` → no-op. `DefaultProjector`'s whole
  purpose is "whatever camera state Arcade already has bound"; pyglet's
  fallback batch draw should use exactly that, unchanged.
- `.get_group_scissor_area()` → always `None` (no group-scoped scissor
  hierarchy to resolve).
- `.projection` / `.view_matrix` (get/set) → thin aliases over the existing
  `self._matrix` state and `ctx.projection_matrix`/`view_matrix`, mirroring
  what pyglet's own `Camera2D` exposes under those names.

**Alternatives considered**: Monkey-patching or wrapping `label.draw()` calls
in `arcade/text.py` to pass pyglet's real `Camera2D` explicitly (reachable
via the private `window._default_camera` attribute, confirmed distinct from
`ArcadeContext._default_camera` — no actual name collision at the storage
level, only at the public-property level) — rejected because `Batch.draw()`
and `Label.draw()` don't accept a camera parameter; reaching this would
require calling several underscore-prefixed pyglet internals
(`Batch._create_draw_context`, `Batch._draw_list`) directly, which is more
fragile and more tightly coupled to pyglet's private implementation than the
small compatibility shim on Arcade's own class.

## 9. FR-011 investigation: the `orthographic_camera` reference-image deviation

**Investigated** (per FR-011, before touching any baseline): the
`orthographic_camera` scene's dev6 render initially differed from its dev3
baseline by 32% of pixels (`tests/unit/rendering/test_dev6_reference_images.py`,
T013). Root-caused by direct pixel-bbox comparison and a from-scratch
matrix/GL-state audit (buffer contents, binding points, program uniform
block bindings were all independently verified correct throughout) down to
one remaining variable: **window resize timing**. `tests/unit/rendering/scenes.py`'s
`_reset()` helper calls `window.set_size(SCENE_WIDTH, SCENE_HEIGHT)` on the
shared test-session window (which starts at 1280x720 per `tests/conftest.py`),
but a resize needs a pass through pyglet's event queue before the window's
viewport/framebuffer actually reflect the new size — `tests/conftest.py`'s
own `prepare_window()` already calls `window.dispatch_pending_events()`
immediately after resizing for exactly this reason, and `scenes.py`'s
`_reset()` was missing that call. Without it, `DefaultProjector` computed its
projection against the *stale* pre-resize viewport.

**Verdict**: benign, and not pyglet-driven at all — a bug in this
migration's own new test harness, introduced by T001/T013, not in Arcade's
rendering code and not a difference between pyglet `dev3` and `dev6`.
**Resolution**: fixed `scenes.py`'s `_reset()` to call
`window.dispatch_pending_events()` after `set_size()` (matching the existing
`conftest.py` convention). No baseline images were regenerated — after the
fix, all four scenes are pixel-identical to their `dev3` baselines
(`diff.getbbox() is None`), so SC-003 is satisfied on the merits, not by
loosening the comparison.

## 10. Full local test suite: pre-existing failures vs. migration regressions

**Investigated**: after all the above fixes, `pytest tests/` on this Windows
machine showed 9 failures + 1 error out of ~1293 collected tests, none of
which involve the camera/UBO/`DefaultProjector` code this migration touches
(they span framebuffer-clear scissor handling, GC reference counting,
geometry buffer assertions, one sprite-render pixel check, a docstring
encoding check, and `test_get_image`'s DPI-scaling assumption). Per FR-007
("the existing automated test suite MUST pass on `dev6`"), the relevant bar
is *no regressions relative to `dev3` on this same machine*, not zero
failures in the abstract — so each was checked against pyglet `3.0.dev3`
(the original `venv/`, left installed for exactly this comparison) before
concluding anything.

**Findings**:
- `tests/unit/test_screenshot.py::test_get_image` and 8 others: **byte-for-byte
  the same failure, reproduced identically on pyglet `3.0.dev3`** in the same
  environment (confirmed by running `venv/Scripts/python.exe -m pytest tests/
  --maxfail=50` against the untouched `dev3` install — same 9 failures + 1
  error, same assertion messages). `test_get_image` specifically fails
  because this machine's 125% Windows display scaling makes the physical
  framebuffer (1000x750) larger than the logical window (800x600); the
  DPI-scaled padding region is left as transparent black `(0,0,0,0)` by
  `window.clear()`, and the test's `image.tobytes()[0:16]` check reads
  exactly that padding, not the actually-cleared content (confirmed via
  `image.getpixel((0,0))` vs `image.getpixel(center)`). This is a
  pre-existing Windows-DPI-scaling gap in the test's assumptions, unrelated
  to pyglet's version — CI never caught it because it runs on Linux/xvfb
  with no DPI scaling, and this is the first time this suite has run against
  real Windows display scaling (Clarifications session 2026-07-16,
  environment correction).
- A handful of others (`test_clear_viewport`, `test_gl_gc` counts,
  `test_gl_geometry` assertions, sprite-render pixels) pass reliably in
  isolation on both `dev3` and `dev6`, and only fail inconsistently as part
  of the full-suite run — consistent with pre-existing order-dependent
  flakiness from the test suite's single shared global window
  (`tests/conftest.py`), not a deterministic pyglet-version-dependent
  regression.
- `test_example_docstrings.py::test_docstrings` fails with a
  `UnicodeDecodeError` reading a `.py` file via `Path.read_text()` with no
  explicit encoding — defaults to the OS locale encoding (`cp1252` on this
  Windows machine) instead of UTF-8. Pyglet-version-independent; would fail
  on any Windows machine whose default codepage can't decode that file,
  regardless of what's installed.

**Verdict**: zero deterministic regressions attributable to the `dev3` →
`dev6` migration. All pre-existing failures are Windows/DPI/test-isolation
gaps that predate this work and are out of scope to fix here.

## 11. Post-review refinement: buffer usage hint

**Raised post-implementation**: is Arcade's new window-block UBO (§1-3, §7)
vulnerable to the same GPU-stall problem pyglet's ring-buffer rewrite was
built to solve? pyglet's own source is explicit about the motivation
(`pyglet/graphics/buffer.py`: *"Do not make the CPU-side data dirty after
binding/committing during the same frame ... or GPU stalls may occur"*) —
rewriting a GPU buffer the driver may still be using for an in-flight draw
forces either a CPU-side stall or an internal reallocation.

**Finding**: legitimate, and it applied to this migration's own new buffer.
`ArcadeContext.__init__` allocated the window-block UBO via
`self.buffer(reserve=128)` — using the default `usage="static"`
(`GL_STATIC_DRAW`), which signals "set once, never touched again" to the
driver, while the actual pattern is "rewritten on every camera activation."
Mismatched usage hints don't cause *incorrect* rendering, but can discourage
drivers from taking the efficient internal-renaming path they'd normally use
for a small, frequently-updated buffer.

**Resolution**: changed to `usage="stream"` (`GL_STREAM_DRAW`), which matches
the actual pattern (write, read briefly, write again) — a one-line change
with no architectural impact. Re-ran `tests/unit/camera`, `tests/unit/window`,
`tests/unit/rendering`, and `tests/integration/test_ubo_stress.py` (131
tests) to confirm no behavioral change.

**Scoped down, not pursued**: replicating pyglet's full N-buffered ring
(2-3 rotating copies) was considered and explicitly not done here. Arcade's
window-block UBO is 128 bytes, updated a handful of times per frame at most
(once per camera activation, not per-object/per-draw-call) — a much smaller
and less frequent workload than what pyglet's general-purpose ring buffer
serves. Without a measured stall, adding rotation logic would be speculative
complexity, and re-introduces exactly the "frames in flight" bookkeeping
this migration's core fix (§2) removed Arcade's dependency on. Revisit only
if profiling on a real workload (e.g. many camera switches per frame — split
screen, multiple render targets) shows an actual stall.

## 12. CI (GitHub Actions, Linux + xvfb) failures on PR #2865 — three real bugs, one non-blocking pre-existing race

CI failed on the first push (`Python 3.11` job), surfacing issues §10's Windows-only local testing couldn't: §10's "confirmed pre-existing, byte-identical on `dev3`" comparison was itself confounded, because both sides of that comparison already included this migration's new test files.

**Bug 1 — reference-image baselines are tied to Windows DPI scaling** (confirmed, fixed): `tests/unit/rendering/test_dev6_reference_images.py` failed with `ValueError: Image size mismatch: (800, 600) != (1000, 750)`. The baseline PNGs were captured on this machine's 125%-scaled Windows display (physical framebuffer 1000x750 for a logical 800x600 window); CI's `xvfb` has no display scaling, so `arcade.get_image()` there returns exactly 800x600. This is a portability bug in the harness itself, not a rendering difference. **Fix**: `tests/unit/rendering/image_compare.py`'s `compare_images()` now resizes the actual capture to the baseline's dimensions (`PIL.Image.Resampling.LANCZOS`) instead of raising on a size mismatch, so the comparison works regardless of the capturing machine's display scaling. Verified locally by downscaling each baseline to 800x600 (simulating an unscaled capture) and confirming it still compares within the SC-003 tolerance.

**Bug 2 — the new stress test leaked TWO separate pieces of global state, not one** (confirmed, fixed — corrected below after further investigation): `tests/integration/test_ubo_stress.py` runs early in collection order (3rd file in the CI job, right after `tests/integration/examples/test_examples.py`), creating and closing 100 windows. This never happens on the unmodified `development` branch (consistently green CI history — checked via `gh run list`), and disappears completely from a local full-suite run when this file is excluded (`pytest tests/ --ignore=tests/integration/test_ubo_stress.py`) — confirming it, not something pre-existing, causes `test_gl_geometry.py`'s `geo.ctx == ctx` assertions (comparing two different `ArcadeContext` instances) and `test_gl_gc.py`'s off-by-one resource counts.

The first fix attempt — saving/restoring `arcade.get_window()` around the churn — was necessary but **not sufficient**, and CI confirmed this: the same failures reappeared on the next push unchanged. Prompted to double check rather than assume a rasterizer difference for the reference-image failures too ("we do similar tests elsewhere without this issue — could there be an actual issue?"), further investigation found the *actual* mechanism: `arcade.gl.Context.__init__` **unconditionally** calls `Context.activate(self)` (`arcade/gl/context.py:214`), setting a **class-level** `Context.active` attribute — a second, completely separate "currently active context" global, independent of `arcade.get_window()`/`set_window()`. Code like `arcade.gl.geometry.quad_2d()` reads `Context.active` directly (`_get_active_context()` in `arcade/gl/geometry.py`, deliberately bypassing `get_window()` since the `gl` module "is forbidden to reach outside of its own module"). Every one of the stress test's 100 window constructions overwrites `Context.active` with its own new context; restoring only `get_window()` left `Context.active` pointed at the last, now-closed, stress window for the rest of the session — exactly matching `test_gl_geometry.py`'s symptom (a geometry object bound to the wrong context) and plausibly `test_gl_gc.py`'s (resource accounting reading from the wrong context too).

**Fix**: both stress test functions now restore *both* globals — `arcade.set_window(window)` and `Context.activate(window.ctx)` — via a single `_restore_global_state()` helper, called both immediately after each window's construction (minimizing how long stress windows are "current" at all) and in a `finally` block at the end. The draw step was also rewritten to use `window.ctx` directly (`_draw_rect_on()`) instead of `arcade.draw_rect_filled()`, so it never depends on either global. **Verified**: a true full-suite local run (`pytest tests/`, matching CI's actual collection order rather than a hand-picked subset, which turned out not to reproduce faithfully — collection order for explicitly-listed paths differs from whole-tree collection) now shows `test_gl_gc`/`test_gl_geometry` passing, converging exactly to the same 5 failures as a run with `test_ubo_stress.py` excluded entirely.

**CI re-run confirmed the fix**: pushing the `Context.active` restoration resolved `test_gl_gc`/`test_gl_geometry`/`test_exp_restricted_input` on the actual CI run (Python 3.14 job) — the full suite now runs to completion (1290 passed vs. 998 before, when it previously stopped early at `--maxfail=10`). Remaining CI failures after that push: `test_gl_framebuffer.py::test_clear_viewport` (present in all three CI runs so far) and the four `test_dev6_reference_images.py` scenes (unchanged ~36% difference) — see Bug 3 below for both.

**Bug 3 — `DefaultProjector`'s scissor shim permanently disables `GL_SCISSOR_TEST` for the whole process** (confirmed, fixed): asked to double-check rather than assume `test_clear_viewport` and the reference-image tests were pre-existing/environmental ("we do similar tests elsewhere without this issue — could there be an actual issue?"), a direct A/B test settled it: running `tests/integration/examples/test_examples.py` + `tests/unit/gl/test_gl_framebuffer.py` together passes cleanly (171 passed) against pyglet `3.0.dev3` with this migration's Arcade code changes already applied, but fails `test_clear_viewport` against `3.0.dev6` with the *identical* Arcade code — isolating the cause to something pyglet-dev6-specific, not a pre-existing Arcade or test-suite issue, and not explained by `Context.active` either (that fix didn't touch it).

Root cause: `arcade/camera/default.py`'s `DefaultProjector.get_group_scissor_area()` (part of the §8 pyglet batch-draw compatibility shim) returned `None`. pyglet's own GL renderer treats `None` as "disable scissor testing entirely" (`pyglet/graphics/api/gl/renderer.py`: `set_scissor(None)` calls `glDisable(GL_SCISSOR_TEST)`), not "no additional restriction." But Arcade enables `GL_SCISSOR_TEST` exactly once, at context creation (`arcade/gl/backends/opengl/context.py`, comment: *"We enable scissor testing by default... always set to the same value as the viewport"*), and never revisits it — it isn't one of the flags `Context.enable`/`disable`/`enable_only` manage. So the *first* pyglet-native draw with no explicit camera anywhere in the whole process — any `arcade.Text`/`draw_text()` call, since those go through `pyglet.text.Label.draw()` — permanently disables scissor testing for every context for the rest of the session, since Arcade has no code path that ever turns it back on. `test_examples.py` runs 136+ examples, essentially guaranteeing at least one hits this. This fully explains `test_clear_viewport` (a viewport-scoped `Framebuffer.clear()` relies on scissor testing being on to restrict the clear), and plausibly the reference-image tests too (broken scissor scoping could produce broad, consistent-looking rendering corruption across every scene) — superseding the earlier "hardware vs. software rasterizer" theory, which was never actually confirmed, just assumed from a consistent-looking percentage across scenes.

**Fix**: `get_group_scissor_area()` now returns `pyglet.window.camera.CameraScissor(*(self._scissor or self.get_current_viewport()))` — a real scissor rectangle matching the current viewport — instead of `None`, so pyglet's renderer calls `glEnable(GL_SCISSOR_TEST)` + `glScissor(...)` (a no-op restriction) rather than disabling the test. **Verified**: the `test_examples.py` + `test_gl_framebuffer.py` combination now passes (171/171) against `3.0.dev6`, and a full local suite run converges to only the same 4 failures that are independently confirmed Windows-only/DPI-related noise absent from every CI run so far (`test_draw_primitives`, `test_render_sprite_solid_pixels`, `test_docstrings`, `test_get_image` — all show the identical "expected color, read `(0,0,0)`" or encoding-locale signature already root-caused in §10/§12 Bug 1, and none of the four appear in any of this PR's three CI runs, whose environment has no display scaling to trigger them).

**Non-blocking, pre-existing, out of scope**: a `PytestUnhandledThreadExceptionWarning` (`AttributeError: 'Window' object has no attribute '_ctx'`, or `GLException` variants) surfaces from `arcade/examples/threaded_loading.py`'s background loading thread calling `get_window().ctx`/raw GL functions from a non-main thread while a new `Window` is mid-construction, or without a context current on that thread at all. Root cause: `Window.__init__` calls `set_window(self)` before `self._ctx` is assigned, and the example's thread is never joined by `test_examples.py`. It doesn't fail CI (no `filterwarnings = error` configured; counted under "warnings," not "failed"/"error"). A defensive `_join_stray_background_threads()` helper was added to the stress test module to reduce (not eliminate) overlap with it, but the underlying thread-hygiene issue in `threaded_loading.py`/`test_examples.py` itself was not fixed — that's a pre-existing bug independent of pyglet version, out of scope for this migration.

## Outcome

All NEEDS CLARIFICATION items from the Technical Context are resolved above.
No open questions block Phase 1 design.
