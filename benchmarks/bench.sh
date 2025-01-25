#!/usr/bin/env bash
# On windows, can run via the bash you get with git:
# C:\Program Files\Git\bin\bash.exe

__dirname="$(CDPATH= cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$__dirname"
cd ..

bench_name="$1"

# I am doing this to ensure it runs against python 3.11, my default install is 3.10
# You can probably remove this line
export PATH="/c/Users/cspot/AppData/Local/Programs/Python/Python311:$PATH"
python.exe --version

# Get current branch name
gitTo=$( git rev-parse --abbrev-ref HEAD )
# Get root of this branch
gitFrom=$( git merge-base origin/development $gitTo )~1
gitCommitRange=$gitFrom..$gitTo

commits=$(git log --format='%H' $gitCommitRange)
commits=$(echo "$commits" | sed -z 's/\n/,/g;s/,$/\n/')
echo "$commits"

hyperfine \
    --show-output \
    --export-markdown benchmarks/results.md \
    --warmup 1 --runs 2 \
    --parameter-list commit "$commits,$commits" \
    --setup 'git checkout {commit}' \
    'python -m benchmarks.'"$bench_name"'.bench {commit}' 

git checkout $gitTo

# Postprocess hyperfine's report to include commit messages and github links
python -c '
import subprocess
import re

report_path = "benchmarks/results.md"
with open(report_path,"r") as file:
    report = file.read()

def replace(x):
    commit = x[1]
    result = subprocess.run(["git", "log", "-n1", "--oneline", commit], capture_output=True, encoding="utf-8")
    message = result.stdout.strip()
    return f"[{message}](https://github.com/pythonarcade/arcade/commit/{commit})"
report = re.sub(r".*? ([a-f0-9]{40})`", replace, report)

with open(report_path,"w") as file:
    file.write(report)
'
