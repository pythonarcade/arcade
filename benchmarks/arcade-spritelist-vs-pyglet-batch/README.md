To run this benchmark, have the companion pyglet branch installed:

```shell
git clone https://github.com/cspotcode/pyglet
cd pyglet
git checkout cspotcode/geosprite_opt
pip install -e .
```

Then from the root directory of your `arcade` clone:

```shell
hyperfine --runs 3 --parameter-list bench pyglet_sprite,pyglet_geosprite,arcade 'python ./benchmarks/arcade-spritelist-vs-pyglet-batch/bench.py {bench}' --show-output
```
