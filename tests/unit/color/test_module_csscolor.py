import sys


def test_csscolors():
    from arcade import csscolor

    names = csscolor.__dict__.keys()

    # py3.15+
    n_extra = int(sys.version_info <= (3, 15))

    # number of colors + 1 import
    assert 156 + n_extra == len(names)
