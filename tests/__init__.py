from doctest import DocTestSuite
from unittest import TestSuite

import arcade

def load_tests(loader, tests, pattern):
    suite = TestSuite()
    suite.addTests(DocTestSuite('arcade.draw_commands'))
    suite.addTests(DocTestSuite('arcade.window_commands'))
    suite.addTests(DocTestSuite('arcade.geometry'))
    suite.addTests(DocTestSuite('arcade.sprite'))
    return suite