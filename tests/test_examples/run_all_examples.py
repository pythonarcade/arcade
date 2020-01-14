"""
Run All Examples

If Python and Arcade are installed, this example can be run from the command line with:
python -m tests.test_examples.run_all_examples
"""
import subprocess
import os
import glob

EXAMPLE_SUBDIR = "../../arcade/examples"


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


def run_examples(indices_in_range, index_skip_list):
    """Run all examples in the arcade/examples directory"""
    examples = _get_examples(EXAMPLE_SUBDIR)
    print("Found {} examples in {}".format(len(examples), EXAMPLE_SUBDIR))

    file_path = os.path.dirname(os.path.abspath(__file__))
    print(file_path)
    os.chdir(file_path+"/../..")
    # run examples
    for (idx, example) in enumerate(examples):
        if indices_in_range is not None and idx not in indices_in_range:
            continue
        if index_skip_list is not None and idx in index_skip_list:
            continue
        print(f"=================== Example {idx + 1:3} of {len(examples)}: {example}")
        # print('%s %s (index #%d of %d)' % ('=' * 20, example, idx, len(examples) - 1))
        cmd = 'python -m ' + example
        subprocess.call(cmd, shell=True)


def all_examples():
    file_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(file_path)

    os.environ['ARCADE_TEST'] = "TRUE"

    indices_in_range = None
    index_skip_list = None
    run_examples(indices_in_range, index_skip_list)


all_examples()
