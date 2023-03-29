"""
Run All tutorials

If Python and Arcade are installed, this tutorial can be run from the command line with:
python -m tests.test_tutorials.run_all_tutorials
"""
import glob
import subprocess
import os
from pathlib import Path

TUTORIAL_SUBDIR = "../../../doc/tutorials/"


def _get_short_name(fullpath):
    return os.path.splitext(os.path.basename(fullpath))[0]

def _get_tutorials(start_path):
    query_path = os.path.join(start_path, "*.py")
    tutorials = glob.glob(query_path)
    tutorials = [_get_short_name(e) for e in tutorials]
    tutorials = [e for e in tutorials if e != "run_all_tutorials"]
    tutorials = [e for e in tutorials if not e.startswith('_')]
    tutorials = [f"doc.tutorials.{start_path.name}." + e for e in tutorials if not e.startswith('_')]
    return tutorials

def run_tutorials(indices_in_range = None, index_skip_list = None):
    """Run all tutorials in the doc/tutorials directory"""
    for tutorial_subdir in [path for path in list(Path.cwd().joinpath(TUTORIAL_SUBDIR).iterdir()) if path.is_dir()]:
        tutorials = _get_tutorials(tutorial_subdir)
        tutorials.sort()
        print(f"Found {len(tutorials)} tutorials in {tutorial_subdir}")

        file_path = os.path.dirname(os.path.abspath(__file__))
        print(file_path)
        os.chdir(file_path+"/../..")
        continue
        # run tutorials
        for (idx, tutorial) in enumerate(tutorials):
            if indices_in_range is not None and idx not in indices_in_range:
                continue
            if index_skip_list is not None and idx in index_skip_list:
                continue
            print(f"=================== tutorial {idx + 1:3} of {len(tutorials)}: {tutorial}")
            # print('%s %s (index #%d of %d)' % ('=' * 20, tutorial, idx, len(tutorials) - 1))

            # Directly call venv, necessary for github action runner
            cmd = 'python -m ' + tutorial

            # print(cmd)
            result = subprocess.check_output(cmd, shell=True)
            if result:
                print(f"ERROR: Got a result of: {result}.")

def all_tutorials():
    file_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(file_path)

    # Set an environment variable that will just run on_update() and on_draw()
    # once, then quit.
    os.environ['ARCADE_TEST'] = "TRUE"

    indices_in_range = None
    index_skip_list = None
    run_tutorials(indices_in_range, index_skip_list)


# all_tutorials()
run_tutorials()
