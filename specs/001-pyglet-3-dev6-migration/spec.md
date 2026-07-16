# Feature Specification: pyglet 3.0.dev6 Migration

**Feature Branch**: `001-pyglet-3-dev6-migration`

**Created**: 2026-07-16

**Status**: Draft

**Input**: User description: "Update to pyglet 3.0.dev6. See the report on some issues with this."

## Clarifications

### Session 2026-07-16

- Q: How should Arcade solve the per-frame ring-buffer UBO growth blocker (Problem 3)? → A: Arcade fully owns its own matrix UBO, independent of pyglet's ring buffer/frame-resource lifecycle.
- Q: How should the spec constrain local (WSL) verification during development? → A: Local runs are limited to a small targeted subset (e.g. specific camera/projector unit tests); the full rendering suite, stress/multi-window runs, and image-comparison acceptance runs are the authoritative gate and execute in a separate GPU-capable environment.
- Q: Once migrated, which pyglet versions must Arcade support? → A: Hard-cut to exactly pyglet 3.0.dev6 (single exact pin); drop dev3/dev4 support, no dual code paths.
- Q: Given the hard-cut to dev6, what is dev4's role in this effort? → A: Drop dev4 entirely; migrate straight from dev3 to dev6 with no dev4 checkpoint.
- Q: Policy when dev6 output differs from reference images beyond existing pixel tolerance? → A: Investigate first; regenerate reference images only for confirmed benign pyglet-driven changes (documented), otherwise treat as a regression to fix in Arcade.

## Overview

Arcade currently pins `pyglet==3.0.dev3`. pyglet has since published `3.0.dev4`,
`3.0.dev5`, and `3.0.dev6`. Between `dev4` and `dev5`, pyglet restructured its
matrix/camera API and changed how the window matrix Uniform Buffer Object (UBO)
is managed, moving to a per-frame ring-buffer resource lifecycle.

Arcade owns its own renderer and matrix handling and does not participate in
pyglet's per-frame resource lifecycle. As documented in the bump report, a naive
version bump to `dev5`/`dev6` causes an unbounded UBO growth crash. Reaching
`dev6` therefore requires adapting Arcade's core rendering/camera integration,
not just changing a pinned version string.

This specification defines the outcome of Arcade running correctly on pyglet
`3.0.dev6`, migrating directly from `3.0.dev3` with no intermediate `dev4` step.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Arcade runs on pyglet 3.0.dev6 without rendering regressions (Priority: P1)

An Arcade application developer upgrades to the Arcade release that depends on
pyglet `3.0.dev6`. Their existing games and tools using cameras, sprites, and
2D/3D projections continue to render correctly and remain stable across many
frames and across multiple window/draw/reset cycles.

**Why this priority**: This is the core goal. Without stable rendering on
`dev6`, the migration delivers no value and cannot ship.

**Independent Test**: Pin pyglet to `3.0.dev6`, run the full existing rendering
test suite (camera, sprite, projection tests) including sequences that create,
draw to, and reset multiple windows. All tests pass with correct pixel output
and no crashes or unbounded resource growth. This authoritative run executes in
a separate GPU-capable environment (not the local WSL dev environment).

**Acceptance Scenarios**:

1. **Given** Arcade is installed with pyglet `3.0.dev6`, **When** an application
   renders sprites and shapes through orthographic and perspective cameras,
   **Then** the rendered output matches the expected reference output produced on
   the prior supported pyglet version.
2. **Given** a test harness that repeatedly creates windows, draws frames, and
   resets state, **When** it runs many cycles in sequence, **Then** the matrix
   UBO does not grow without bound and no "Growing UniformBufferObject" warnings
   or memory-related crashes occur.
3. **Given** an Arcade application on `dev6`, **When** it changes view,
   projection, or viewport at runtime, **Then** the changes take effect correctly
   on the next draw.

---

### User Story 2 - Camera/matrix integration adapted to pyglet's new API (Priority: P1)

A maintainer needs Arcade's camera and context layers updated so that the matrix
UBO location, the `view`/`projection`/`viewport` delegation to pyglet's
`default_camera`, and the per-frame UBO lifecycle are all reconciled with
pyglet's `dev5`+ design without breaking Arcade's own `DefaultProjector`.

**Why this priority**: This is the enabling technical work that makes User Story
1 possible. It is required for `dev6` support. Because Arcade hard-cuts directly
from `dev3` to `dev6`, this integration work must be completed as part of the same
migration rather than deferred behind an intermediate release.

**Independent Test**: With pyglet at `dev6`, unit tests for the orthographic
projector, perspective projector, and 2D camera pass, and window/context
construction completes without `AttributeError` on the `default_camera` name
collision.

**Acceptance Scenarios**:

1. **Given** pyglet reads the window matrix UBO from the default camera's view
   storage, **When** Arcade's context initializes, **Then** it binds the correct
   UBO from the new location.
2. **Given** pyglet routes `window.view`/`window.projection`/`window.viewport`
   through `default_camera`, **When** Arcade sets matrices, **Then** Arcade's own
   `DefaultProjector` is preserved and window/context construction does not raise
   `AttributeError: 'Window' object has no attribute '_ctx'`.
3. **Given** repeated matrix binds during rendering, **When** frames are drawn,
   **Then** reserved UBO ranges are released so buffer size stays bounded.

### Edge Cases

- What happens when multiple windows are created and destroyed in one process
  (the scenario that triggers unbounded UBO growth today)?
- What happens during offscreen/headless rendering where Arcade does not drive
  pyglet's normal frame loop?
- How does Arcade behave if a consuming application drives its own render loop
  and never signals pyglet frame boundaries?
- What happens if an application still references `window._matrices` directly
  (removed in `dev5`+)?
- How is the transition handled for downstream users pinned to a range of pyglet
  versions that spans the API break between `dev4` and `dev5`?
- What happens when `dev6` rendering differs from current reference images beyond
  the existing pixel tolerance — is it a benign pyglet-driven change or an Arcade
  regression?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Arcade MUST declare an exact dependency on pyglet `3.0.dev6`
  (`pyglet==3.0.dev6`) as its sole supported pyglet version once migration is
  complete. Support for `3.0.dev3`/`3.0.dev4` is dropped, and no
  conditional/dual code paths across the `dev4→dev5` API break are introduced.
- **FR-002**: Arcade MUST read the window matrix UBO from pyglet's current
  location (the default camera's view storage) rather than the removed
  `window._matrices.ubo`.
- **FR-003**: Arcade MUST preserve its own default projector behavior even though
  pyglet now delegates `view`/`projection`/`viewport` through its
  `default_camera`, without name-collision failures during window/context
  construction.
- **FR-004**: Arcade MUST route its matrix writes (view and projection) through a
  path compatible with pyglet `dev5`+ so that orthographic, perspective, and 2D
  cameras produce correct output.
- **FR-005**: Arcade MUST keep the matrix UBO size bounded across repeated matrix
  binds, window/draw/reset cycles, and multi-window sessions, with no unbounded
  growth and no memory-related crash. Arcade MUST achieve this by fully owning
  its own matrix UBO independent of pyglet's ring-buffer/frame-resource lifecycle,
  rather than relying on or driving pyglet's per-frame resource lifecycle.
- **FR-006**: Arcade MUST render visually correct output on `dev6` equivalent to
  the previously supported pyglet version for existing camera, sprite, and shape
  workflows.
- **FR-007**: The existing automated test suite (including camera, sprite, and
  projection tests, and sequential multi-file rendering runs) MUST pass on
  `dev6`.
- **FR-008**: Arcade MUST document any changed public/behavioral expectations
  arising from pyglet's matrix/camera API change so downstream users can adapt.
- **FR-011**: When `dev6` rendered output deviates from existing reference images
  beyond the current pixel tolerance, the deviation MUST be investigated before
  any re-baselining. Reference images MUST be regenerated only for deviations
  confirmed as intended/benign pyglet-driven changes, and such regenerations MUST
  be documented; all other deviations MUST be treated as regressions to fix in
  Arcade.
- **FR-009**: The migration MUST leave the working tree buildable and installable
  (dependency resolution succeeds) at pyglet `3.0.dev6`.
- **FR-010**: Verification MUST distinguish between local development checks and
  authoritative acceptance checks. Local (WSL) verification is limited to a small
  targeted subset of tests (e.g. specific camera/projector unit tests). The full
  rendering test suite, stress/multi-window runs, and image-comparison acceptance
  runs (SC-001 through SC-003) MUST be executed in a separate GPU-capable
  environment, which is the authoritative gate for the migration.

### Key Entities *(include if feature involves data)*

- **Matrix UBO (Uniform Buffer Object)**: GPU buffer holding view/projection
  matrices. In pyglet `dev5`+ it lives on the default camera's view storage and
  is managed via a rotating ring buffer with a per-frame resource lifecycle.
- **Default Camera / Default Projector**: pyglet's `default_camera` now owns
  view/projection/viewport. Arcade overrides `default_camera` with its own
  `DefaultProjector`; these two must coexist.
- **Camera types**: Orthographic projector, perspective projector, and 2D camera
  — each writes matrices and must remain correct after the API change.
- **Frame-resource lifecycle**: pyglet's mechanism that reserves and frees UBO
  ranges per frame. Arcade does not drive this lifecycle and instead owns its own
  matrix UBO to remain independent of it, keeping buffer growth bounded.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With pyglet pinned to `3.0.dev6`, 100% of the existing rendering
  and camera test suite passes, including sequential multi-file runs that
  currently trigger the crash.
- **SC-002**: Running a stress sequence of at least 100 window/draw/reset cycles
  produces zero "Growing UniformBufferObject" warnings and no crash, and matrix
  UBO memory usage stabilizes rather than doubling per bind.
- **SC-003**: Rendered output for the standard camera, sprite, and shape test
  scenarios matches the pre-migration reference output within the project's
  existing image-comparison tolerance. Any deviation beyond tolerance is
  investigated and either fixed as a regression or, only if confirmed benign and
  pyglet-driven, resolved by a documented reference-image regeneration.
- **SC-004**: A clean environment install resolves and installs Arcade with
  pyglet `3.0.dev6` successfully.
- **SC-005**: SC-001 through SC-003 (full suite, stress/multi-window, and
  image-comparison outcomes) are demonstrated in a separate GPU-capable
  environment; the local WSL environment is used only for a small targeted subset
  of tests and is not treated as the acceptance gate.

## Assumptions

- The findings in the bump report are accurate: the API break occurs between
  pyglet `dev4` and `dev5`, `dev4` still exposes `window._matrices`, and the
  unbounded UBO growth is caused by an architectural mismatch with pyglet's
  per-frame resource lifecycle.
- The target end state is pyglet `3.0.dev6` (latest at time of writing); no newer
  pyglet dev release needs to be supported by this effort.
- Correct rendering is validated against the project's existing image-comparison
  test infrastructure and reference images.
- The local development environment is WSL with limited graphics capability, so
  it is used only for a small targeted subset of tests. The full suite,
  stress/multi-window runs, and image-comparison acceptance runs are executed in a
  separate GPU-capable environment which serves as the authoritative acceptance
  gate.
- Arcade migrates directly from pyglet `3.0.dev3` to `3.0.dev6` with no `dev4`
  intermediate checkpoint or release.
- The project constitution template is unpopulated, so no additional
  project-specific governance constraints apply beyond standard Arcade
  contribution practices (tests must pass, no rendering regressions).
- The UBO lifecycle blocker will be solved by Arcade fully owning its own matrix
  UBO independent of pyglet's ring buffer (chosen over adopting pyglet's
  frame-resource lifecycle), so Arcade does not need to drive pyglet's per-frame
  resource lifecycle.
