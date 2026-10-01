# Collision benchmarks

Run these from the repository root, e.g. `python -m benchmarks.collisions.micro`.
Each script prints which arcade it imported, so you can check it isn't
testing a different installed copy.

| Script | What it does |
|---|---|
| `bench.py` | Simulates bullets bouncing around walls for a minute, with a window. Used by `benchmarks/bench.sh` to time each commit on a branch with hyperfine. |
| `micro.py` | Time per call for `check_for_collision` on single pairs (boxes, octagons, rotated, near-misses), on sprites that move or rotate every call, and for `check_for_collision_with_list`. |
| `hit_box.py` | Time for hit box `left`/`right`/`bottom`/`top`, `get_adjusted_bounds()`, and recalculating adjusted points at different angles. |
| `compare_reference.py` | Not a benchmark: a correctness check. Compares `check_for_collision` with a simple reference on 200,000 random sprite pairs (`--pairs` and `--seed` change this). Exits with an error if any results differ. |

See also `benchmarks/spatial_hash/queries.py` for spatial hash query timing.

## Comparing two versions

Run the same script on each version (for example on `development` and on
your branch) and compare the output. Timings change between runs, often by
5-10% and much more if other programs are busy, so:

- Run each version more than once, and close CPU-heavy programs.
- Check that unchanged cases (such as "box/box far apart") give similar
  times on both versions before trusting differences elsewhere.

Collision changes can give different results on different platforms. For
example `sin(pi / 4)` is `0.7071067811865476` on Windows but
`0.7071067811865475` on Linux, which can matter for exactly touching sprites.
CI runs on Linux.
