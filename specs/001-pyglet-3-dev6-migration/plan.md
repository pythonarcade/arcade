# Implementation Plan: pyglet 3.0.dev6 Migration

**Branch**: `001-pyglet-3-dev6-migration` | **Date**: 2026-07-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-pyglet-3-dev6-migration/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Migrate Arcade's pinned pyglet dependency directly from `3.0.dev3` to
`3.0.dev6` (no `dev4` intermediate). pyglet `dev5`+ removed
`window._matrices` and moved window view/projection/viewport onto a lazily
created `default_camera` (`pyglet.window.camera.camera2d.Camera2D`) backed by
a per-frame ring-buffer UBO. A naive version bump crashes immediately with
`AttributeError: 'Window' object has no attribute '_matrices'` (confirmed by
reproduction at `arcade/context.py:62`), and — before this fix — would have
caused unbounded UBO growth once past that point, because Arcade drives its
own render loop and over-subscribes pyglet's ring buffer relative to its
frame-in-flight slots. The technical approach (confirmed against the actual
pyglet dev6 source, see research.md) is: (1) have `ArcadeContext` allocate
and own a single fixed-size (128-byte) window-block UBO directly, using its
own existing `Buffer.bind_to_uniform_block()` at GL binding point 0 —
independent of pyglet's `Camera2D` ring buffer entirely, so growth is
impossible by construction; and (2) route `OrthographicProjector`,
`PerspectiveProjector`, and Arcade's `Camera2D` matrix writes through
`ctx.projection_matrix`/`ctx.view_matrix` instead of pyglet's own
`window.projection`/`window.view` properties — a second, previously
undocumented bug discovered during implementation (see data-model.md "Camera
types"), needed because these two paths no longer share a buffer once Arcade
owns its own. A third predicted failure mode — an `AttributeError` from a
`default_camera` property name collision during `Window.__init__` — was
investigated (research.md §4) but did not reproduce against the actual
pyglet dev6 build, so no fix was needed for it. Verification runs the full
existing test suite plus a new stress test and a new minimal reference-image
comparison harness, authoritatively on a native Windows development machine,
in addition to (not instead of) the project's existing unchanged Linux+xvfb
CI.

## Technical Context

**Language/Version**: Python (project supports 3.10–3.14; CI matrix tests all of them; no version-specific behavior introduced by this migration)

**Primary Dependencies**: `pyglet==3.0.dev6` (replacing `pyglet==3.0.dev3`, exact pin, `pyproject.toml:25`); Arcade's own `arcade.gl` OpenGL wrapper (self-contained, not built on the `moderngl` PyPI package — unchanged by this migration); `Pillow` (already a dependency, used for the new reference-image comparison harness — no new third-party dependency required)

**Storage**: N/A (no persisted application data; GPU buffer objects are runtime-only)

**Testing**: `pytest`, run via `uv run pytest`; existing suites under `tests/unit/camera/`, `tests/unit/window/`, `tests/unit/test_screenshot.py`, `tests/integration/examples/`, `tests/integration/tutorials/`; a new minimal reference-image comparison module is added (no existing image-diff harness was found — see research.md §5)

**Target Platform**: Cross-platform library (Windows/Linux/macOS, plus WebGL backend); authoritative test execution for this migration is native Windows (developer machine) per Clarifications, in addition to the existing Linux+xvfb CI matrix (Python 3.10–3.14) which is unchanged

**Project Type**: Library (2D game/graphics framework built on pyglet) — single-project structure, no frontend/backend split

**Performance Goals**: No new performance target beyond parity with pre-migration behavior; window-block UBO memory usage must stabilize rather than grow (SC-002) — satisfied by construction via a single fixed-size buffer (data-model.md)

**Constraints**: Exact single-version pyglet pin (`3.0.dev6`), no dual code paths across the `dev4`→`dev5` API break (FR-001); GL binding point 0 is reserved by pyglet for its own `WindowBlock` at the shader-introspection level, so Arcade's own UBO must be (re)bound via the existing raw `glBindBufferRange` mechanism rather than pyglet's `UniformBlock.set_binding()` (research.md §3)

**Scale/Scope**: Touches `arcade/context.py`, `arcade/gl/backends/opengl/context.py`, `arcade/gl/backends/webgl/context.py`, `arcade/camera/orthographic.py`, `arcade/camera/perspective.py`, `arcade/camera/camera_2d.py` (matrix-write call sites redirected to `ctx.projection_matrix`/`ctx.view_matrix`, discovered during implementation), and adds new test modules for reference-image comparison and UBO-growth stress testing; `arcade/application.py` needed no change (research.md §4)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is an unfilled template (all
`[PRINCIPLE_N_NAME]`/`[SECTION_N_NAME]` placeholders, no ratified content) —
there are no project-specific constitutional gates to evaluate. This matches
the spec's own Assumptions section. No violations to justify; Complexity
Tracking below is empty.

**Post-Phase-1 re-check**: Unchanged — Phase 1 design (data-model.md,
contracts/public-api-contract.md, quickstart.md) introduces no new
architectural surface beyond what's already described here (an internally
owned UBO and a reordered constructor), so there is nothing new to gate
against the still-unpopulated constitution. PASS.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
arcade/
├── context.py                       # ArcadeContext: owns the window-block UBO (modified)
├── application.py                   # Window: construction order fix for default_camera (modified)
├── camera/
│   ├── default.py                   # DefaultProjector (unmodified contract, verified by tests)
│   ├── static.py                    # unmodified contract
│   └── ...                          # OrthographicProjector, PerspectiveProjector, Camera2D (unmodified contracts)
├── gl/
│   └── backends/
│       ├── opengl/context.py        # OpenGLArcadeContext.bind_window_block() (modified)
│       └── webgl/context.py         # WebGL mirror of bind_window_block() (modified)
└── ...                              # rest of the library, unaffected

tests/
├── unit/
│   ├── camera/                      # existing camera/projector unit tests (must keep passing)
│   ├── window/                      # existing window construction tests (must keep passing)
│   └── test_screenshot.py           # existing pixel/framebuffer read primitives, reused by new harness
├── integration/
│   ├── examples/test_examples.py    # sequential multi-window smoke run (reproduces UBO-growth scenario)
│   └── tutorials/test_tutorials.py  # same, tutorials
└── unit/rendering/                  # NEW: minimal reference-image comparison harness (SC-003/FR-011),
    └── test_dev6_reference_images.py    exact filename/location finalized in tasks.md

pyproject.toml                       # pyglet version pin (modified: dev3 → dev6)
CHANGELOG.md                         # documentation obligation (FR-008)
.github/workflows/test.yml           # UNCHANGED — existing Linux+xvfb CI, runs alongside local Windows gate
```

**Structure Decision**: Single-project library structure (Arcade is already
organized this way; no new top-level directories are introduced). This is a
targeted, in-place migration touching a small, well-identified set of
existing files (`arcade/context.py`, `arcade/application.py`, the two GL
backend `context.py` files) plus one new test module — not a restructuring.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations — table intentionally left empty (unpopulated constitution,
no gates to fail).
