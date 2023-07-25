To run this benchmark, from the root directory:

```shell
hyperfine --runs 3 --parameter-list bench pyglet,arcade 'python ./benchmarks/arcade-spritelist-vs-pyglet-batch/bench.py {bench}' --show-output
```