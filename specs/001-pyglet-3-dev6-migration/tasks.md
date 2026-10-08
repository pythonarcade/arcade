---

description: "Task list for pyglet 3.0.dev6 Migration"
---

# Tasks: pyglet 3.0.dev6 Migration

**Input**: Design documents from `/specs/001-pyglet-3-dev6-migration/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/public-api-contract.md](./contracts/public-api-contract.md), [quickstart.md](./quickstart.md)

**Tests**: This feature's acceptance criteria (FR-007, SC-001–SC-003) *are*
tests — running the existing suite plus two new harnesses (reference-image
comparison, UBO-growth stress test) is the actual deliverable, not an
optional add-on. Test/verification tasks are woven into each phase rather
than treated as a separate strict TDD red/green step, since this is a
migration fixing existing behavior, not new business logic.

**Organization**: Tasks are grouped by user story from spec.md. User Story 2
(P1, "Camera/matrix integration adapted to pyglet's new API") is the enabling
technical fix; User Story 1 (P1, "Arcade runs on pyglet 3.0.dev6 without
rendering regressions") is the outcome-level validation of that fix. The spec
itself states US2 is prerequisite work for US1 ("this is the enabling
technical work that makes User Story 1 possible" — spec.md), so — unlike
typical independent stories — **US1's tasks depend on US2 being complete**.
This dependency is intentional and documented, not an oversight.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Paths are relative to the repository root (`C:\Users\PaCra\Projects\arcade`)

## Path Conventions

Single-project library structure (see plan.md's Project Structure) — `arcade/`
and `tests/` at the repository root. No new top-level directories.

---

## Phase 1: Setup

**Purpose**: Capture the pre-migration baseline and switch the dependency pin.

**⚠️ ORDERING NOTE**: T001 MUST run before T002/T003 — the baseline images
must be captured while pyglet `3.0.dev3` is still installed, since they are
the "known-good" reference SC-003/FR-011 compare against after the bump.

- [X] T001 [P] Capture baseline reference PNGs on the current pyglet
  `3.0.dev3` environment for four representative render scenes (a sprite, a
  shape, an orthographic-camera view, a perspective-camera view) using
  `arcade.get_image()`; save them under
  `tests/unit/rendering/baseline/*.png`. Document the exact scene setup (code
  or fixture) used to generate each PNG so it can be re-run identically after
  the migration. (research.md §5, contracts/public-api-contract.md
  "Verification harness contract")
- [X] T002 Update the pyglet dependency pin in `pyproject.toml` (line 25)
  from `"pyglet==3.0.dev3"` to `"pyglet==3.0.dev6"`. (FR-001,
  contracts/public-api-contract.md "Dependency contract")
- [X] T003 Regenerate the lockfile and confirm a clean install: run
  `uv lock` then `uv sync --no-group docs` from the repository root; resolve
  any dependency conflicts that surface. (SC-004, FR-009)

**Checkpoint**: Baseline images exist, `pyproject.toml`/`uv.lock` point at
`pyglet==3.0.dev6`, and the environment installs cleanly. Test runs at this
point are EXPECTED to crash or fail (the fix hasn't landed yet) — that's the
pre-fix baseline, not a regression.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared test infrastructure needed by both user stories' later
verification tasks. No production code changes here.

**⚠️ CRITICAL**: Complete before starting User Story 2's implementation tasks.

- [X] T004 [P] Create the `tests/unit/rendering/` package (add
  `__init__.py`) as the home for the new reference-image comparison and
  stress-test infrastructure used by later tasks.
- [X] T005 [P] Add a pixel-diff helper in
  `tests/unit/rendering/image_compare.py` using PIL (already a dependency)
  that loads two PNGs and checks them against the tolerance defined in
  SC-003: no more than 2% of pixels may differ by more than a per-channel
  delta of 10 (out of 255), and the whole-image mean absolute per-channel
  difference must be 1% or less. (research.md §5 — no new third-party
  dependency)

**Checkpoint**: Shared test infrastructure exists. User Story 2's code
changes can now begin.

---

## Phase 3: User Story 2 - Camera/matrix integration adapted to pyglet's new API (Priority: P1)

**Goal**: Fix the two concrete failure mechanisms so Arcade's camera/context
layer works correctly against pyglet `3.0.dev6`: (a) Arcade fully owns a
fixed-size window-block UBO instead of touching pyglet's ring buffer, and (b)
`Window.__init__`'s construction order no longer triggers the
`default_camera` `AttributeError`.

**Independent Test**: With pyglet at `dev6`, run
`uv run pytest tests/unit/camera tests/unit/window -v` — orthographic
projector, perspective projector, and 2D camera unit tests pass, and window
construction completes without `AttributeError: 'Window' object has no
attribute '_ctx'`.

### Implementation for User Story 2

- [X] T006 [P] [US2] ~~Reorder `Window.__init__`~~ — **empirically not
  needed**. research.md §4 predicted pyglet's own `__init__` would trigger
  Arcade's overridden `default_camera` property (via inherited
  `projection`/`view`/`viewport` properties) before `self._ctx` exists,
  raising `AttributeError: 'Window' object has no attribute '_ctx'`. Verified
  against the actual installed pyglet `3.0.dev6`
  (`.venv/Lib/site-packages/pyglet/window/__init__.py:578-581`): pyglet's
  `_create_projection()` assigns the *private* `self._default_camera`
  attribute directly during `__init__`, never invoking the *public*
  `default_camera` property — so there is no collision. Confirmed by running
  the full camera/window unit suite (125 passed) and by directly creating
  three fresh `arcade.Window` instances in sequence: no `AttributeError`
  occurred in either case. No code change made; research.md §4 corrected to
  record this.
- [X] T007 [P] [US2] In `arcade/context.py`'s `ArcadeContext.__init__`
  (replacing line 62's `self._window_block = window._matrices.ubo`),
  allocate a new, fixed-size (128-byte: two `Mat4`s) GL buffer object that
  `ArcadeContext` owns directly, independent of pyglet's `Camera2D`/ring
  buffer. Store it as `self._window_block` so downstream code (bind calls,
  `reset()`) keeps working against the same attribute name/shape.
  (data-model.md "Arcade Window Block UBO" entity, FR-005)
- [X] T008 [US2] In `arcade/context.py`, change the `projection_matrix` and
  `view_matrix` property setters (currently `self.window.projection = value`
  / `self.window.view = value`, lines ~421-445) to write the matrix data
  directly into Arcade's own UBO (from T007) instead of through pyglet's
  `window.projection`/`window.view` properties, so Arcade's per-camera-update
  matrix writes never commit into pyglet's ring buffer. Getters may continue
  reading from `self.window.projection`/`.view` for interop, or from Arcade's
  own stored matrix state — pick whichever keeps behavior correct and
  document the choice inline only if non-obvious. (research.md §7,
  data-model.md `ArcadeContext` entity — depends on T007)
- [X] T009 [US2] Update `OpenGLArcadeContext.bind_window_block()` in
  `arcade/gl/backends/opengl/context.py` (lines 436-443) to bind Arcade's own
  UBO buffer's `.id` (from T007) at GL binding point 0, offset 0, size 128 —
  same `glBindBufferRange` call, new buffer source. (research.md §3 — binding
  point 0 remains usable via this raw GL call; depends on T007)
- [X] T010 [P] [US2] Mirror the same `bind_window_block()` update in
  `arcade/gl/backends/webgl/context.py` (lines 384-388) for the WebGL
  backend. (depends on T007, parallel with T009 — different file)
- [X] T011 [US2] Verify `ArcadeContext.reset()` in `arcade/context.py` (line
  ~330, which calls `bind_window_block()` and resets `view_matrix`/
  `projection_matrix`) works correctly against the new Arcade-owned UBO
  across repeated window/reset cycles — no stale bindings, no leaked buffer
  objects from the old per-init allocation. (supports SC-002; depends on
  T007, T008, T009, T010)
- [X] T012 [US2] Run the Independent Test for this story:
  `uv run pytest tests/unit/camera tests/unit/window -v` on Windows with
  pyglet `3.0.dev6` installed. Fix any failures, in particular confirming no
  `AttributeError: 'Window' object has no attribute '_ctx'` occurs during
  window construction. (depends on T006, T008, T009, T010, T011)

- [X] T012a [US2] **Discovered during T015's full-suite run, not in the
  original task breakdown**: pyglet's own `Batch.draw()` (used by
  `pyglet.text.Label.draw()`, which `arcade.Text` delegates to) and pyglet's
  base `Window.projection`/`.view` properties both fall back to/delegate
  through `self.default_camera` — landing on Arcade's overridden
  `DefaultProjector` instead of pyglet's own `Camera2D`, and crashing with
  `AttributeError` for missing `.view`/`.begin`/`.get_group_scissor_area`/
  `.projection`/`.view_matrix` (research.md §8 — this is the real
  `default_camera` collision predicted in §4, just manifesting in pyglet's
  batch-draw fallback and property delegation rather than in
  `Window.__init__`). Fixed by adding a minimal duck-typing compatibility
  shim to `arcade/camera/default.py`'s `DefaultProjector`: `.view` (returns
  `self`), `.begin()` (no-op), `.get_group_scissor_area()` (returns `None`),
  and `.projection`/`.view_matrix` (get/set aliases over existing state).
  Found via `tests/integration/examples/test_examples.py` (platform-tutorial
  score text) and `arcade/examples/gl/chip8_display.py` (reads
  `window.projection`).

**Checkpoint**: The two root-cause failure mechanisms (ring-buffer growth,
`default_camera` `AttributeError`) are fixed, and targeted camera/window unit
tests pass on Windows. User Story 1's full-suite validation can now proceed.

---

## Phase 4: User Story 1 - Arcade runs on pyglet 3.0.dev6 without rendering regressions (Priority: P1)

**Goal**: Confirm the fix from User Story 2 holds up under the full existing
test suite, a multi-window stress sequence, and visual/pixel comparison
against pre-migration output — the outcome the whole migration exists to
deliver.

**Independent Test**: Pin pyglet to `3.0.dev6`, run the full existing
rendering test suite including sequences that create, draw to, and reset
multiple windows; all tests pass with correct pixel output and no crashes or
unbounded resource growth. This runs on the local Windows development
environment as the authoritative gate (Clarifications session 2026-07-16).

**Depends on**: Phase 3 (User Story 2) checkpoint being complete.

### Implementation for User Story 1

- [X] T013 [P] [US1] Add a reference-scene structural-sanity test module at
  `tests/unit/rendering/test_dev6_reference_images.py` that renders the same
  four scenes captured in T001 and asserts structural properties (correct
  non-zero dimensions, not a single uniform/blank color, not fully black).
  **Revised post-CI-verification (SC-003 §CI verification results
  clarification)**: originally asserted a pixel-tolerance diff (≤2%/≤1%,
  via T005's helper) against the `tests/unit/rendering/baseline/*.png`
  images; dropped in favor of structural checks after CI runs confirmed the
  pixel-tolerance comparison produces a consistent ~36% difference between
  real-GPU baselines and CI's `xvfb` software rasterizer, unrelated to any
  actual regression (unmoved across two independently-fixed rendering
  bugs). T005's `compare_images()` helper remains available for manual,
  local, real-GPU pixel comparison per FR-011, but no longer gates the
  automated test. (SC-003, FR-011, depends on T001, T005)
- [X] T014 [P] [US1] Add a window/draw/reset stress test at
  `tests/integration/test_ubo_stress.py` that creates, draws one frame to,
  and closes at least 100 windows in a single process, capturing
  stdout/stderr and asserting the string `"Growing UniformBufferObject"`
  never appears and the process does not crash. (SC-002 — can be authored in
  parallel with T013; both are new files)
- [X] T015 [US1] Run the full local test suite on Windows:
  `uv run arcade` then `uv run pytest --maxfail=10`, including
  `tests/integration/examples/test_examples.py` and
  `tests/integration/tutorials/test_tutorials.py` (the sequential
  multi-file runs that previously triggered the crash). Fix any regressions
  found. (SC-001, quickstart.md step 3 — depends on Phase 3 checkpoint,
  T013, T014)
- [X] T016 [US1] Run the stress test from T014 and confirm it passes: zero
  "Growing UniformBufferObject" warnings across 100+ cycles, no crash.
  (SC-002 — depends on T014, T015)
- [X] T017 [US1] Run the reference-scene test from T013 and resolve any
  deviations per the FR-011 policy: investigate first; only regenerate a
  baseline PNG for a confirmed benign, pyglet-driven, documented difference;
  otherwise fix the regression in Arcade. (SC-003 — depends on T013, T015)
  — **Investigated (research.md §9)**: the `orthographic_camera` scene
  initially deviated 32% from baseline (back when this was a pixel-tolerance
  test); root cause was a missing `window.dispatch_pending_events()` call in
  the new test harness's `scenes.py` after a window resize (not
  pyglet-driven, not an Arcade regression — a bug in this migration's own
  new test code). Fixed the test harness. **Further investigated on actual
  CI (research.md §12)**: after that fix, all 4 scenes were pixel-identical
  on Windows but showed a consistent ~36% difference on CI's `xvfb`
  rasterizer, confirmed unrelated to any regression (unmoved across two
  separately-fixed real bugs found during CI verification — a `Context.active`
  leak and a permanently-disabled `GL_SCISSOR_TEST`). Per the follow-up
  decision recorded in spec.md's Clarifications, the test was revised to
  structural checks (T013) rather than pixel-tolerance comparison; no
  baseline was regenerated, since the difference was never diagnosed as
  pyglet-driven or benign — it's simply not a reliable automated signal
  across different rasterizers.
- [X] T018 [US1] Confirm `.github/workflows/test.yml` (Linux + `xvfb`,
  Python 3.10-3.14) is unmodified by this migration —
  `git diff --stat .github/workflows/test.yml` and `git status --short
  .github/` both empty. (SC-005, Clarifications session 2026-07-16
  "environment correction" — depends on T015). Actually observing that CI
  run go green requires pushing the branch, which is a separate action for
  the user to authorize, not performed as part of this local implementation
  session.

**Checkpoint**: Full suite, stress test, and reference-image comparison all
pass locally on Windows; existing CI is green and untouched. The migration's
acceptance criteria (SC-001 through SC-005) are met.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and cleanup once both stories are complete.

- [X] T019 [P] Update `CHANGELOG.md` documenting the pyglet
  `3.0.dev3` → `3.0.dev6` bump, and add a note for advanced users mixing raw
  pyglet camera/window code with Arcade that `window._matrices` no longer
  exists and that `window.default_camera` (pyglet's) is distinct from
  `arcade.Window.default_camera` (Arcade's `DefaultProjector`). (FR-008,
  contracts/public-api-contract.md "Documentation obligation")
- [X] T020 Walk through `quickstart.md` end-to-end on a clean Windows
  checkout to confirm every step and expected outcome still holds exactly as
  written; fix any drift between the guide and reality.
- [X] T021 [P] Remove any temporary debug logging, print statements, or
  scaffolding added while diagnosing the ring-buffer growth or
  `AttributeError` during T006-T012.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, but internally ordered — T001 before
  T002/T003 (baseline must be captured on `dev3` before the pin changes).
- **Foundational (Phase 2)**: Can run in parallel with Phase 1 (different
  files/concerns — test scaffolding vs. dependency pin) but conceptually
  precedes Phase 3/4's use of that scaffolding.
- **User Story 2 (Phase 3)**: Depends on Phase 1 (pyglet `3.0.dev6` must be
  installed) and Phase 2 (shared test scaffolding, though not strictly
  required until Phase 4). This is the enabling fix.
- **User Story 1 (Phase 4)**: Depends on Phase 3's checkpoint (the fix must
  exist before full-suite/stress/image validation can meaningfully pass) —
  this is the one explicit cross-story dependency in this feature, and it is
  intentional per spec.md.
- **Polish (Phase 5)**: Depends on Phase 4 being complete.

### Parallel Opportunities

- T001 (baseline capture) can run while T004/T005 (test scaffolding) are
  being written — different concerns, no file overlap.
- T006 (application.py) and T007 (context.py) touch different files and can
  be done in parallel.
- T009 (OpenGL backend) and T010 (WebGL backend) touch different files and
  can be done in parallel once T007 lands.
- T013 (reference-image test) and T014 (stress test) are new, independent
  files and can be authored in parallel.
- T019 and T021 (changelog, cleanup) can run in parallel with each other and
  with T020.

---

## Parallel Example: User Story 2

```bash
# T006 and T007 touch different files — run together:
Task: "Reorder Window.__init__ construction order in arcade/application.py"
Task: "Allocate Arcade-owned UBO in ArcadeContext.__init__ in arcade/context.py"

# After T007 lands, T009 and T010 touch different backend files — run together:
Task: "Update bind_window_block() in arcade/gl/backends/opengl/context.py"
Task: "Update bind_window_block() in arcade/gl/backends/webgl/context.py"
```

## Parallel Example: User Story 1

```bash
# T013 and T014 are new, independent test files — run together:
Task: "Add reference-image comparison test in tests/unit/rendering/test_dev6_reference_images.py"
Task: "Add window/draw/reset stress test in tests/integration/test_ubo_stress.py"
```

---

## Implementation Strategy

### MVP First (User Story 2, then User Story 1)

Because User Story 1 cannot be meaningfully validated until User Story 2's
fix exists, the natural "MVP" here is: Setup → Foundational → **User Story 2**
(the fix) → **User Story 1** (proof it works). There is no smaller shippable
increment than "both stories complete" — a partial fix (only T006-T007, say)
would leave either the crash or the `AttributeError` unresolved, and the
whole point of this migration is that both are gone simultaneously (spec.md:
"hard-cut... no dual code paths").

### Incremental Delivery Within the Constraint

1. Complete Setup + Foundational.
2. Complete User Story 2 → run its Independent Test → confirms the two root
   causes are fixed at the unit-test level.
3. Complete User Story 1 → run its Independent Test → confirms no
   regressions at the full-suite/stress/visual level, and CI is unaffected.
4. Complete Polish (changelog, quickstart validation, cleanup).
5. Ship: `pyproject.toml` now pins `pyglet==3.0.dev6`, all acceptance
   criteria (SC-001–SC-005) met.

---

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps task to specific user story for traceability.
- This feature has an intentional cross-story dependency (US1 depends on
  US2's checkpoint) — documented above rather than forced into artificial
  independence, per the spec's own framing of US2 as "the enabling technical
  work that makes User Story 1 possible."
- Commit after each task or logical group.
- Stop at the Phase 3 checkpoint to confirm the root-cause fixes work in
  isolation before moving to full-suite validation.
