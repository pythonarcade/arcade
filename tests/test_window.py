from unittest import TestCase


class TestWindow(TestCase):

    def test_allows_minimum_size(self):
        import arcade
        window = arcade.Window(200, 100, resizable=True)
        window.set_min_size(200, 200)
        window.close()

    def test_disallows_minimum_size(self):
        import arcade
        window = arcade.Window(200, 100, resizable=False)
        self.assertRaises(ValueError, window.set_min_size, 200, 200)
        window.close()

    def test_allows_maximum_size(self):
        import arcade
        window = arcade.Window(200, 100, resizable=True)
        window.set_max_size(200, 200)
        window.close()

    def test_disallows_maximum_size(self):
        import arcade
        window = arcade.Window(200, 100, resizable=False)
        self.assertRaises(ValueError, window.set_max_size, 200, 200)
        window.close()

    # def test_set_size_location(self):
    #     import arcade
    #     window = arcade.Window(200, 100, resizable=True)
    #     window.set_size(900, 800)
    #     self.assertEqual(window.width, 900)
    #     self.assertEqual(window.height, 800)
    #     window.close()
