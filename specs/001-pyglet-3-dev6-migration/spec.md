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

### Session 2026-07-16 (environment correction)

- Q: The prior clarification assumed a WSL dev environment with limited graphics capability, requiring the authoritative test run to happen in a separate GPU-capable environment. Development actually happens on native Windows. Does this change the verification approach? → A: Yes. Native Windows has full OpenGL/GPU capability, so the full rendering test suite, stress/multi-window runs, and image-comparison acceptance runs execute directly in the local Windows development environment. No separate GPU-capable environment is required; the local environment is now the authoritative gate.
- Q: The project's existing CI (`.github/workflows/test.yml`) already runs the full pytest suite on `ubuntu-latest` with `xvfb` (headless software rendering) on every push/PR. How does local Windows verification relate to that existing CI gate? → A: Local Windows execution is the developer's authoritative full-fidelity check for this migration (replacing the prior WSL limitation); the existing Linux+xvfb CI continues unchanged as the standard automated gate for every PR/push. Both must pass; CI is not replaced or reworked by this migration.

### Editorial correction 2026-07-16 (post-/speckit-analyze)

- FR-002 and the "Matrix UBO" Key Entity bullet originally described Arcade reading its window matrix UBO *from* pyglet's `default_camera` location — a design superseded by the Clarifications session's FR-005 decision (Arcade fully owns an independent UBO) but never updated to match, leaving the two requirements in direct contradiction. FR-002 and the Key Entity bullet below are corrected to reflect the FR-005 design that plan.md/data-model.md/tasks.md already implement; no new decision was made, this only propagates the existing one.
- SC-003/FR-011 originally referred to "the project's existing image-comparison tolerance," but no such tolerance or harness existed prior to this migration (research.md §5). SC-003/FR-011 are corrected to state a concrete tolerance established by this migration's new reference-image harness instead of an implied pre-existing one.

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
and no crashes or unbounded resource growth. This authoritative run executes
directly in the local Windows development environment, which has full
OpenGL/GPU capability.

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
- **FR-002**: Arcade MUST NOT depend on pyglet's `window._matrices.ubo`
  (removed in `dev5`+) or on any other pyglet-internal storage location for
  its window matrix UBO. Instead, per FR-005, Arcade MUST allocate and own
  its own window matrix UBO directly, independent of pyglet's
  `default_camera`-managed ring buffer, while still producing
  view/projection/viewport values equivalent to what pyglet's own
  `default_camera` would produce for the same camera state.
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
- **FR-011**: When `dev6` rendered output deviates from the reference images
  beyond the tolerance defined in SC-003, the deviation MUST be investigated
  before any re-baselining. Reference images MUST be regenerated only for deviations
  confirmed as intended/benign pyglet-driven changes, and such regenerations MUST
  be documented; all other deviations MUST be treated as regressions to fix in
  Arcade.
- **FR-009**: The migration MUST leave the working tree buildable and installable
  (dependency resolution succeeds) at pyglet `3.0.dev6`.
- **FR-010**: Verification MUST be executable in the local Windows development
  environment, which has full OpenGL/GPU capability. The full rendering test
  suite, stress/multi-window runs, and image-comparison acceptance runs
  (SC-001 through SC-003) MUST be executed and pass locally on Windows as the
  developer's authoritative full-fidelity check; no separate GPU-capable
  environment is required beyond this. This is in addition to, not a
  replacement for, the project's existing Linux+xvfb CI pipeline, which
  continues to run the automated test suite unchanged on every push/PR. Both
  the local Windows run and the existing CI run MUST pass.

### Key Entities *(include if feature involves data)*

- **Matrix UBO (Uniform Buffer Object)**: GPU buffer holding view/projection
  matrices. pyglet `dev5`+ moved its own internal window matrix UBO onto the
  default camera's view storage, managed via a rotating ring buffer with a
  per-frame resource lifecycle — this is pyglet's own mechanism, separate
  from Arcade's. Arcade instead allocates and owns a distinct, fixed-size
  matrix UBO independent of pyglet's ring buffer (see FR-005); this is the
  buffer Arcade's own shaders/rendering pipeline actually read from.
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
  scenarios matches the pre-migration reference output within a defined
  tolerance — no more than 2% of pixels may differ from the baseline by more
  than a per-channel delta of 10 (out of 255), and the whole-image mean
  absolute per-channel difference must be 1% or less. This tolerance is
  established by this migration's new reference-image harness (no such
  harness or tolerance existed prior to this migration). Any deviation beyond
  tolerance is investigated and either fixed as a regression or, only if
  confirmed benign and pyglet-driven, resolved by a documented reference-image
  regeneration.
- **SC-004**: A clean environment install resolves and installs Arcade with
  pyglet `3.0.dev6` successfully.
- **SC-005**: SC-001 through SC-003 (full suite, stress/multi-window, and
  image-comparison outcomes) are demonstrated directly in the local Windows
  development environment, which serves as the developer's authoritative
  full-fidelity acceptance gate; no separate GPU-capable environment is
  required. The project's existing Linux+xvfb CI pipeline continues to run the
  automated test suite unchanged on every push/PR as an additional,
  independent gate.

## Assumptions

- The findings in the bump report are accurate: the API break occurs between
  pyglet `dev4` and `dev5`, `dev4` still exposes `window._matrices`, and the
  unbounded UBO growth is caused by an architectural mismatch with pyglet's
  per-frame resource lifecycle.
- The target end state is pyglet `3.0.dev6` (latest at time of writing); no newer
  pyglet dev release needs to be supported by this effort.
- Correct rendering is validated against the project's existing image-comparison
  test infrastructure and reference images.
- The local development environment is native Windows with full OpenGL/GPU
  capability, so the full test suite, stress/multi-window runs, and
  image-comparison acceptance runs can be executed and serve as the
  developer's authoritative full-fidelity acceptance gate directly in the
  local environment. No separate GPU-capable environment is required.
- The project's existing Linux+xvfb CI pipeline (`.github/workflows/test.yml`)
  is out of scope for this migration to change; it continues to run the
  automated test suite unchanged on every push/PR alongside (not instead of)
  local Windows verification.
- Arcade migrates directly from pyglet `3.0.dev3` to `3.0.dev6` with no `dev4`
  intermediate checkpoint or release.
- The project constitution template is unpopulated, so no additional
  project-specific governance constraints apply beyond standard Arcade
  contribution practices (tests must pass, no rendering regressions).
- The UBO lifecycle blocker will be solved by Arcade fully owning its own matrix
  UBO independent of pyglet's ring buffer (chosen over adopting pyglet's
  frame-resource lifecycle), so Arcade does not need to drive pyglet's per-frame
  resource lifecycle.
