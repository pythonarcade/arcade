import sys


def test_colors():
    from arcade import color

    names = color.__dict__.keys()

    # py3.15
    n_extra = int(sys.version_info <= (3, 15))

    # number of colors + 1 real import
    assert 1016 + n_extra == len(names)
