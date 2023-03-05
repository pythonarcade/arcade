"""
Run All Examples

If Python and Arcade are installed, this example can be run from the command line with:
python -m tests.test_examples.run_all_examples
"""
import pyglet
import glob
import os
import subprocess

import pytest

EXAMPLE_SUBDIR = "../../../arcade/examples"
# These examples are allowed to print to stdout
ALLOW_STDOUT = set([
    "arcade.examples.dual_stick_shooter",
])

def _get_short_name(fullpath):
    return os.path.splitext(os.path.basename(fullpath))[0]


def _get_examples(start_path):
    query_path = os.path.join(start_path, "*.py")
    examples = glob.glob(query_path)
    examples = [_get_short_name(e) for e in examples]
    examples = [e for e in examples if e != "run_all_examples"]
    examples = [e for e in examples if not e.startswith('_')]
    examples = ["arcade.examples." + e for e in examples if not e.startswith('_')]
    return examples


def find_examples(indices_in_range, index_skip_list):
    """List all examples in the arcade/examples directory"""
    examples = _get_examples(EXAMPLE_SUBDIR)
    examples.sort()
    print(f"Found {len(examples)} examples in {EXAMPLE_SUBDIR}")

    file_path = os.path.dirname(os.path.abspath(__file__))
    print(file_path)
    os.chdir(f"{file_path}/../..")

    for (idx, example) in enumerate(examples):
        if indices_in_range is not None and idx not in indices_in_range:
            continue
        if index_skip_list is not None and idx in index_skip_list:
            continue

        allow_stdout = example in ALLOW_STDOUT
        yield f'python -m {example}', allow_stdout


def list_examples(indices_in_range, index_skip_list):
    file_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(file_path)

    return list(find_examples(indices_in_range, index_skip_list))


@pytest.mark.parametrize(
    "cmd, allow_stdout",
    argvalues=list_examples(
        indices_in_range=None,
        index_skip_list=None
    )
)
def test_all(cmd, allow_stdout):
    # Set an environment variable that will just run on_update() and on_draw()
    # once, then quit.
    import pyglet
    test_env = os.environ.copy()
    test_env["ARCADE_TEST"] = "TRUE"

    result = subprocess.check_output(cmd, shell=True, env=test_env)
    if result and not allow_stdout:
        print(f"ERROR: Got a result of: {result}.")
        assert not result
