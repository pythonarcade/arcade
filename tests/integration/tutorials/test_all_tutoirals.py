"""
Run All tutorials

If Python and Arcade are installed, this tutorial can be run from the command line with:
python -m tests.test_tutorials.test_all_tutorials
"""
import glob
import os
import subprocess
from pathlib import Path

import pytest

TUTORIAL_SUBDIR = "../../../doc/tutorials/"
# These tutorials are allowed to print to stdout
ALLOW_STDOUT = set()

def _get_short_name(fullpath):
    return os.path.splitext(os.path.basename(fullpath))[0]

def _get_tutorials(start_path):
    query_path = os.path.join(start_path, "*.py")
    tutorials = glob.glob(query_path)
    tutorials = [_get_short_name(e) for e in tutorials]
    tutorials = [e for e in tutorials if e != "run_all_tutorials"]
    tutorials = [e for e in tutorials if not e.startswith('_')]
    tutorials = [f"{e}.py" for e in tutorials if not e.startswith('_')]
    return tutorials

def find_tutorials(indices_in_range, index_skip_list):
    """List all tutorials in the doc/tutorials directory"""
    file_dir = Path(__file__).parent
    for tutorial_subdir in [path for path in list((file_dir / TUTORIAL_SUBDIR).iterdir()) if path.is_dir()]:
        tutorials = _get_tutorials(tutorial_subdir)
        tutorials.sort()
        print(f"Found {len(tutorials)} tutorials in {tutorial_subdir}")
        if len(tutorials) == 0:
            continue
        print(tutorial_subdir)
        # os.chdir(tutorial_subdir)
        for (idx, tutorial) in enumerate(tutorials):
            if indices_in_range is not None and idx not in indices_in_range:
                continue
            if index_skip_list is not None and idx in index_skip_list:
                continue

            allow_stdout = tutorial in ALLOW_STDOUT
            yield f'python {tutorial}', allow_stdout, tutorial_subdir
        # os.chdir("../")         


def list_tutorials(indices_in_range, index_skip_list):
    file_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(file_path)

    return list(find_tutorials(indices_in_range, index_skip_list))


@pytest.mark.parametrize(
    "cmd, allow_stdout, tutorial_subdir",
    argvalues=list_tutorials(
        indices_in_range=None,
        index_skip_list=None
    )
)
def test_all(cmd, allow_stdout, tutorial_subdir):
    # Set an environment variable that will just run on_update() and on_draw()
    # once, then quit.
    import pyglet
    test_env = os.environ.copy()
    test_env["ARCADE_TEST"] = "TRUE"
    os.chdir(tutorial_subdir)
    result = subprocess.check_output(cmd, shell=True, env=test_env)
    if result and not allow_stdout:
        print(f"ERROR: Got a result of: {result}.")
        assert not result
