# import pytest
# import arcade
#
#
# class FakeWindow(arcade.Window):
#     """A test double Window that is never displayed"""
#
#     def __init__(self):
#         super().__init__()
#         # Track the behavior of Views:
#         self.draw_calls = []  # records sequence of calls to on_draw()
#         self.update_calls = []  # records sequence of calls to update()
#         self.mouse_motion_calls = []  # records sequence of calls to on_mouse_motion()
#
#     def set_visible(self, visible=True):
#         pass  # Make set_visible do nothing for testing
#
#     def test(self, frames: int = 10):
#         """The order of the event loop in the original Window.test method
#         was producing unintuitive results for the purpose of these tests.
#         """
#         for i in range(frames):
#             self.switch_to()
#             self.update(1 / 60)
#             self.dispatch_event('on_draw')
#             self.dispatch_events()
#             self.flip()
#
#
# class BaseView(arcade.View):
#     def update(self, delta_time):
#         self.window.update_calls.append(self.__class__.__name__)
#         self.window.dispatch_event("on_mouse_motion", 42, 43, 1, 1)  # change
#
#     def on_draw(self):
#         self.window.draw_calls.append(self.__class__.__name__)
#
#
# class ViewOne(BaseView):
#     def on_mouse_motion(self, _x, _y, _dx, _dy):
#         self.window.mouse_motion_calls.append(self.__class__.__name__)
#
#
# class ViewTwo(BaseView):
#     pass
#
#
# def test_it_asserts_showing_view_of_none():
#     win = FakeWindow()
#     with pytest.raises(Exception):
#         # noinspection PyTypeChecker
#         win.show_view(None)
#
#
# def test_single_view():
#     win = FakeWindow()
#     view = ViewOne()
#     win.show_view(view)
#     win.test(2)
#     assert win.update_calls == ['ViewOne', 'ViewOne']
#     assert win.draw_calls == ['ViewOne', 'ViewOne']
#     assert win.mouse_motion_calls == ['ViewOne', 'ViewOne']
#
#
# def test_multiple_views():
#     win = FakeWindow()
#     view_one = ViewOne()
#     view_two = ViewTwo()
#     win.show_view(view_one)
#     win.test(2)
#     win.show_view(view_two)
#     win.test(1)
#     win.show_view(view_one)
#     win.test(2)
#     assert win.update_calls == ['ViewOne', 'ViewOne', 'ViewTwo', 'ViewOne', 'ViewOne']
#     assert win.draw_calls == ['ViewOne', 'ViewOne', 'ViewTwo', 'ViewOne', 'ViewOne']
#
#
# def test_show_view_improper_argument_raises_value_error():
#     window = FakeWindow()
#
#     with pytest.raises(ValueError):
#         # noinspection PyTypeChecker
#         window.show_view(None)
#
#
# # def test_show_view_sets_window_if_none():
# #     window = FakeWindow()
# #     view_one = ViewOne()
# #     assert view_one.window is None
# #
# #     window.show_view(view_one)
# #     assert view_one.window is window
# #
# #
# # def test_show_view_does_not_allow_multiple_windows_of_one_view_object():
# #     window1 = FakeWindow()
# #     window2 = FakeWindow()
# #     view_one = ViewOne()
# #
# #     window1.show_view(view_one)
# #     assert view_one.window is window1
# #
# #     with pytest.raises(RuntimeError):
# #         window2.show_view(view_one)
