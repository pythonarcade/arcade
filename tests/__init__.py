from doctest import DocTestSuite
from unittest import TestSuite
from unittest import TextTestRunner

import arcade


def load_tests(loader=None, tests=None, pattern=None):
    suite = TestSuite()
    suite.addTests(DocTestSuite('arcade.draw_commands'))
    suite.addTests(DocTestSuite('arcade.window_commands'))
    suite.addTests(DocTestSuite('arcade.geometry'))
    suite.addTests(DocTestSuite('arcade.sprite'))
    suite.addTests(DocTestSuite('arcade.application'))
    suite.addTests(DocTestSuite('arcade.sound'))
    return suite

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(load_tests())
