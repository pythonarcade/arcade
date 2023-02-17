#!/usr/bin/env bash
# On windows, can run via the bash you get with git:
# C:\Program Files\Git\bin\bash.exe

__dirname="$(CDPATH= cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$__dirname"
cd ..

bench_name="$1"

python.exe --version

hyperfine \
    --show-output \
    --export-markdown benchmarks/results.md \
    --warmup 1 --runs 2 \
    --parameter-list shapely 'enabled,disabled' \
    'bash ./benchmarks/bench-shapely-helper.sh '"$bench_name"' {shapely}'
