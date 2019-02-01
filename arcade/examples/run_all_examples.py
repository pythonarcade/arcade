"""
Run All Examples

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.run_all_examples
"""
import subprocess
import argparse
import os
import glob

EXAMPLE_SUBDIR = "arcade/examples"

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

    # run examples
    for (idx, example) in enumerate(examples):
        if indices_in_range is not None and idx not in indices_in_range:
            continue
        if index_skip_list is not None and idx in index_skip_list:
            continue
        print('%s %s (index #%d of %d)' % ('=' * 20, example, idx, len(examples) - 1))
        cmd = 'python -m ' + example
        subprocess.call(cmd, shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--range", nargs=2, metavar=("LO", "HI"),
                        help="range of indexes, inclusive")
    parser.add_argument("--skip", nargs="*", metavar="IDX",
                        help="list of indexes to skip")
    args = parser.parse_args()
    if args.range is not None:
        args.range = range(int(args.range[0]), int(args.range[1]) + 1)
    if args.skip is not None:
        args.skip = [int(i) for i in args.skip]
    run_examples(args.range, args.skip)