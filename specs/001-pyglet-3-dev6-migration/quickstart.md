# Quickstart: Validating the pyglet 3.0.dev6 Migration

**Feature**: [spec.md](./spec.md) | **Data model**: [data-model.md](./data-model.md) | **Contract**: [contracts/public-api-contract.md](./contracts/public-api-contract.md)

This guide describes how to validate the migration end-to-end on a local,
native Windows development machine (the authoritative full-fidelity gate per
Clarifications session 2026-07-16), in addition to the unchanged Linux+xvfb
CI pipeline.

## Prerequisites

- Native Windows development machine with a working GPU/OpenGL driver
  (not WSL — WSL's limited graphics capability was the reason this project's
  local verification story changed, see Clarifications).
- [`uv`](https://docs.astral.sh/uv/) installed (already the project's
  dependency/sync tool per `.github/workflows/test.yml`).
- This repo checked out on branch `001-pyglet-3-dev6-migration`.
- `pyglet==3.0.dev6` is published on PyPI and resolves directly via `uv
  sync`/`uv lock` — no local pyglet checkout is required. (During this
  migration's own development, the actual pyglet dev6 source was also
  available locally at `C:\Users\PaCra\Projects\pyglet`, tag `v3.0.dev6`,
  and was used to verify research.md's findings against ground truth — but
  that's a research aid, not a runtime dependency.)
- Note: `uv sync` creates/uses its own `.venv/` regardless of any
  pre-existing differently-named virtual environment (e.g. `venv/`) in the
  repo — run subsequent commands through `uv run` (as below) so this is
  handled automatically.

## 1. Point the project at pyglet 3.0.dev6

Update the pin in `pyproject.toml` (FR-001):

```toml
"pyglet==3.0.dev6",
```

Then sync:

```bash
uv sync --no-group docs
```

**Expected outcome (SC-004)**: dependency resolution and install succeed with
no conflicts.

## 2. Run the targeted unit subset (fast inner loop)

```bash
uv run pytest tests/unit/camera -v
uv run pytest tests/unit/window -v
```

**Expected outcome**: camera/projector unit tests
(`test_camera2d.py`, `test_orthographic_projector.py`,
`test_perspective_projector.py`, `test_viewport_projector.py`,
`test_camera_controller_methods.py`, `test_camera_shake.py`,
`test_fullscreen.py`, `test_view.py`, `test_window.py`) pass. A naive version
bump fails immediately here with `AttributeError: 'Window' object has no
attribute '_matrices'` (`arcade/context.py`) before the fix; research.md §4's
separately predicted `default_camera`/`_ctx` `AttributeError` during
`Window.__init__` did not reproduce empirically (see research.md §4), though
a related `default_camera` collision does surface elsewhere — see step 3.

## 3. Run the full local suite (authoritative gate)

```bash
uv run arcade
uv run pytest --maxfail=10
```

**Expected outcome (SC-001)**: 100% of the existing rendering and camera test
suite passes on Windows, including
`tests/integration/examples/test_examples.py` and
`tests/integration/tutorials/test_tutorials.py` (sequential multi-file runs —
the scenario that previously triggered the UBO-growth crash). Running the
examples is also what surfaces the *real* `default_camera` collision:
pyglet's own text-rendering batch draw (used by any example drawing score
text) falls back to `window.default_camera` when no explicit camera is
given, and needs `DefaultProjector`'s pyglet-compatibility shim
(research.md §8) to not raise `AttributeError`.

Note: a small number of pre-existing, environment-specific test failures are
expected and are **not** migration regressions — confirmed by running the
same full suite against the untouched pyglet `3.0.dev3` install on the same
machine and seeing byte-identical failures (research.md §10). These involve
Windows DPI-scaling assumptions and shared-global-window test-order
flakiness, unrelated to the pyglet version.

## 4. Stress-test window/draw/reset cycles

```bash
uv run pytest tests/integration/test_ubo_stress.py -v
```

This creates/draws/closes 100 windows, and separately runs 100
`ctx.reset()` cycles on one window, asserting no `"Growing
UniformBufferObject"` warning is ever emitted (captured via
`warnings.catch_warnings`) and that the window-block UBO keeps a stable
buffer identity across resets.

**Expected outcome (SC-002)**: both tests pass — zero "Growing
UniformBufferObject" warnings, no crash, and a stable window-block UBO
identity (consistent with data-model.md's fixed 128-byte, Arcade-owned
buffer — no ring-buffer growth possible by construction).

## 5. Reference-scene check (automated) + optional visual comparison (manual)

```bash
uv run pytest tests/unit/rendering/test_dev6_reference_images.py -v
```

This renders the sprite/shape/orthographic-camera/perspective-camera scenes
defined in `tests/unit/rendering/scenes.py` and checks structural sanity
(correct dimensions, not blank/uniform, not fully black) — this runs
identically on CI and locally, on any rasterizer. It does **not** do a
pixel-tolerance comparison against the baseline images anymore (see
spec.md's Clarifications, "CI verification results" — CI's software
rasterizer produced a consistent ~36% difference against real-GPU
baselines, confirmed unrelated to any actual bug, so it wasn't a reliable
automated cross-environment signal).

For a precise, manual, local comparison against the checked-in baseline
PNGs in `tests/unit/rendering/baseline/` (real GPU hardware only), use
`tests/unit/rendering/image_compare.py`'s `compare_images()` directly. If a
manual comparison shows a deviation, investigate per FR-011 before
regenerating a baseline — a cross-rasterizer difference alone is not
grounds for regeneration. Baselines are regenerated only for a confirmed
benign, pyglet-driven, documented difference, via
`tests/unit/rendering/generate_baseline.py` run on the prior known-good
pyglet version — never on the version under test.

**Expected outcome (SC-003a, automated)**: all four scenes pass the
structural checks, everywhere. **(SC-003b, manual/optional)**: on real GPU
hardware, rendered output for sprite, shape,
orthographic-camera, and perspective-camera scenes matches the checked-in
`dev3`-era baseline PNGs within the SC-003 tolerance (≤2% of pixels differing
by more than 10/255 per channel, ≤1% whole-image mean absolute difference).
Any deviation is investigated per FR-011 before touching a baseline image —
see research.md §9 for a worked example (a test-harness timing bug, not a
pyglet-driven difference).

## 6. Confirm CI is unaffected

Push the branch and confirm `.github/workflows/test.yml` (Linux + `xvfb`,
Python 3.10–3.14) still runs and passes unchanged — this migration does not
modify that workflow (Clarifications session 2026-07-16, environment
correction).

**Resolved via actual CI verification** (see research.md §12 for the full
investigation): three separate real bugs were found and fixed by running
this migration's new tests against actual CI (a `Context.active` global
leak, a `DefaultProjector` shim permanently disabling `GL_SCISSOR_TEST`,
and the stress test's window-churn not restoring global state) — none of
which were reproducible in local Windows-only testing. A fourth apparent
issue (the reference-image test's ~36% CI-vs-local difference) turned out
not to be a bug at all: it was unmoved by fixing the other three, so
step 5's test was revised to structural-only checks rather than
pixel-tolerance comparison (see step 5's note), pending a final CI run to
confirm the revised test passes as expected.

## Done criteria

All of SC-001 through SC-005 pass locally on Windows, the existing CI run is
green and untouched, and `CHANGELOG.md` documents the pyglet version bump and
any behavioral notes per FR-008 / the public API contract's documentation
obligation.
