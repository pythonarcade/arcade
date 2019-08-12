import unittest
import arcade


class _FakeWindow(arcade.Window):
    """A test double Window that is never displayed"""
    def __init__(self):
        super().__init__()
        # Tracking behavior of _FakeView:
        self.draw_calls = []  # list that records sequence of calls to on_draw()
        self.update_calls = []  # list that records sequence of calls to update()

    def set_visible(self, visible=True):
        pass  # Make set_visible do nothing for testing


class _MockView(arcade.View):
    """A test double View that records when a View's on_draw and update methods are called"""
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.next_view = None
        self.count = 0

    def on_draw(self):
        self.window.draw_calls.append(self.name)

    def update(self, delta_time):
        self.window.update_calls.append(self.name)

        self.count += 1
        if self.count == 3:
            self.count = 0
            self.window.show_view(self.next_view)


class TestView(unittest.TestCase):
    def test_it_asserts_showing_view_of_none(self):
        win = _FakeWindow()
        with self.assertRaises(Exception):
            win.show_view(None)

    def test_single_view(self):
        win = _FakeWindow()
        view = _MockView('a')
        win.show_view(view)
        win.test(5)
        self.assertEqual(['a', 'a', 'a', 'a', 'a'], win.update_calls)
        self.assertEqual(['a', 'a', 'a', 'a'], win.draw_calls)  # the first frame has an update but no draw

    def test_multiple_views(self):
        win = _FakeWindow()
        view_a = _MockView('a')
        view_b = _MockView('b')
        view_a.next_view = view_b
        view_b.next_view = view_a
        win.show_view(view_a)
        win.test(10)
        self.assertEqual(['a', 'a', 'a', 'b', 'b', 'b', 'a', 'a', 'a', 'b'], win.update_calls)
        self.assertEqual(['a', 'a', 'b', 'b', 'b', 'a', 'a', 'a', 'b'], win.draw_calls) # the first frame has an update but no draw


if __name__ == '__main__':
    unittest.main()
