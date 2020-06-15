from unittest.mock import call

import arcade
from arcade.gui import TextButton, Theme


def test_create_text_button_with_minimal_params():
    button = TextButton(center_x=50, center_y=20, width=30, height=10,
                        text='Click me')

    assert button.text == 'Click me'

    assert button.center_x == 50
    assert button.center_y == 20
    assert button.width == 30
    assert button.height == 10

    assert button.pressed is False
    assert button.active is True


def test_setup_button_font_with_theme():
    theme = Theme()
    button = TextButton(center_x=50, center_y=20, width=30, height=10,
                        text='Click me', theme=theme)
    assert button.font is theme.font


def test_setup_button_font_without_theme():
    button = TextButton(center_x=50, center_y=20, width=30, height=10,
                        text='Click me', font_size=10, font_face="Arial",
                        font_color=arcade.color.GREEN)

    assert button.font.size == 10
    assert button.font.name == "Arial"
    assert button.font.color == arcade.color.GREEN


def test_get_border_positions():
    button = TextButton(center_x=50, center_y=20, width=30, height=10,
                        text='Click me')
    assert button.get_top() == 20 + 10 / 2
    assert button.get_bottom() == 20 - 10 / 2
    assert button.get_left() == 50 - 30 / 2
    assert button.get_right() == 50 + 30 / 2


def test_check_mouse_collision():
    button = TextButton(center_x=50, center_y=20, width=30, height=10,
                        text='Click me')

    assert button.check_mouse_collision(x=50, y=20) is True

    assert button.check_mouse_collision(x=35, y=20) is True
    assert button.check_mouse_collision(x=34, y=20) is False
    assert button.check_mouse_collision(x=65, y=20) is True
    assert button.check_mouse_collision(x=66, y=20) is False

    assert button.check_mouse_collision(x=50, y=25) is True
    assert button.check_mouse_collision(x=50, y=26) is False
    assert button.check_mouse_collision(x=50, y=15) is True
    assert button.check_mouse_collision(x=50, y=14) is False


def test_on_press():

    class Counter:
        def __init__(self):
            self.value = 0

        def update(self):
            self.value += 1

    button = TextButton(center_x=50, center_y=20, width=30, height=10,
                        text='Click me')

    counter = Counter()
    button.press_action = counter.update
    button.on_press()
    assert counter.value == 1


def test_on_release():

    class Counter:
        def __init__(self):
            self.value = 0

        def update(self):
            self.value += 2

    button = TextButton(center_x=50, center_y=20, width=30, height=10,
                        text='Click me')

    counter = Counter()
    button.release_action = counter.update
    button.on_release()
    assert counter.value == 2


def test_on_click():

    class Counter:
        def __init__(self):
            self.value = 0

        def update(self):
            self.value += 3

    button = TextButton(center_x=50, center_y=20, width=30, height=10,
                        text='Click me')

    counter = Counter()
    button.click_action = counter.update
    button.on_click()
    assert counter.value == 3


def test_check_mouse_press_when_check_mouse_collision_true(mocker):
    mocker.patch.object(TextButton, 'check_mouse_collision',
                        return_value=True)
    mocker.patch.object(TextButton, 'on_press')
    button = TextButton(center_x=50, center_y=20, width=30, height=10,
                        text='Click me')
    button.check_mouse_press(50, 20)

    assert button.pressed is True
    button.check_mouse_collision.assert_called_once_with(50, 20)
    button.on_press.assert_called_once()


def test_check_mouse_press_when_check_mouse_collision_false(mocker):
    mocker.patch.object(TextButton, 'check_mouse_collision',
                        return_value=False)
    mocker.patch.object(TextButton, 'on_press')
    button = TextButton(center_x=50, center_y=20, width=30, height=10,
                        text='Click me')
    button.check_mouse_press(0, 1)

    assert button.pressed is False
    button.check_mouse_collision.assert_called_once_with(0, 1)
    button.on_press.assert_not_called()


def test_check_mouse_release_when_pressed_is_false(mocker):
    mocker.patch.object(TextButton, 'check_mouse_collision',
                        return_value=True)
    mocker.patch.object(TextButton, 'on_release')
    mocker.patch.object(TextButton, 'on_click')
    button = TextButton(center_x=50, center_y=20, width=30, height=10,
                        text='Click me')
    button.check_mouse_release(50, 20)

    assert button.pressed is False
    button.check_mouse_collision.assert_not_called()
    button.on_release.assert_not_called()
    button.on_click.assert_not_called()


def test_check_mouse_release_when_pressed_is_true_and_check_mouse_collision_true(mocker):
    mocker.patch.object(TextButton, 'check_mouse_collision',
                        return_value=True)
    mocker.patch.object(TextButton, 'on_release')
    mocker.patch.object(TextButton, 'on_click')
    button = TextButton(center_x=50, center_y=20, width=30, height=10,
                        text='Click me')
    button.pressed = True
    button.check_mouse_release(50, 20)

    assert button.pressed is False
    button.check_mouse_collision.assert_called_once_with(50, 20)
    button.on_release.assert_called_once()
    button.on_click.assert_called_once()


def test_check_mouse_release_when_pressed_is_true_and_check_mouse_collision_false(mocker):
    mocker.patch.object(TextButton, 'check_mouse_collision',
                        return_value=False)
    mocker.patch.object(TextButton, 'on_release')
    mocker.patch.object(TextButton, 'on_click')
    button = TextButton(center_x=50, center_y=20, width=30, height=10,
                        text='Click me')
    button.pressed = True
    button.check_mouse_release(0, 1)

    assert button.pressed is False
    button.check_mouse_collision.assert_called_once_with(0, 1)
    button.on_release.assert_not_called()
    button.on_click.assert_not_called()


def test_draw_when_theme_not_set(mocker):
    mocker.patch.object(TextButton, 'draw_texture_theme')
    mocker.patch.object(TextButton, 'draw_color_theme')
    mocker.patch('arcade.draw_text')

    button = TextButton(center_x=50, center_y=20, width=30, height=10,
                        text='Click me')
    button.draw()
    button.draw_color_theme.assert_called_once()
    button.draw_texture_theme.assert_not_called()
    arcade.draw_text.assert_called_once_with('Click me', 50, 20,
                                             button.font.color,
                                             font_size=button.font.size,
                                             font_name=button.font.name,
                                             width=button.width,
                                             align="center",
                                             anchor_x="center",
                                             anchor_y="center")


def test_draw_when_theme_set(mocker):
    mocker.patch.object(TextButton, 'draw_texture_theme')
    mocker.patch.object(TextButton, 'draw_color_theme')
    mocker.patch('arcade.draw_text')

    button = TextButton(center_x=50, center_y=20, width=30, height=10,
                        text='Click me', theme=Theme())
    button.draw()
    button.draw_color_theme.assert_not_called()
    button.draw_texture_theme.assert_called_once()
    arcade.draw_text.assert_called_once_with('Click me', 50, 20,
                                             button.font.color,
                                             font_size=button.font.size,
                                             font_name=button.font.name,
                                             width=button.width,
                                             align="center",
                                             anchor_x="center",
                                             anchor_y="center")


def test_draw_when_theme_not_set_and_text_is_empty(mocker):
    mocker.patch.object(TextButton, 'draw_texture_theme')
    mocker.patch.object(TextButton, 'draw_color_theme')
    mocker.patch('arcade.draw_text')

    button = TextButton(center_x=50, center_y=20, width=30, height=10, text='')
    button.draw()
    button.draw_color_theme.assert_called_once()
    button.draw_texture_theme.assert_not_called()
    arcade.draw_text.assert_not_called()


def test_draw_when_theme_set_and_text_is_empty(mocker):
    mocker.patch.object(TextButton, 'draw_texture_theme')
    mocker.patch.object(TextButton, 'draw_color_theme')
    mocker.patch('arcade.draw_text')

    button = TextButton(center_x=50, center_y=20, width=30, height=10, text='',
                        theme=Theme())
    button.draw()
    button.draw_color_theme.assert_not_called()
    button.draw_texture_theme.assert_called_once()
    arcade.draw_text.assert_not_called()


def test_draw_texture_theme(mocker):
    mocker.patch('arcade.draw_texture_rectangle')

    theme = arcade.gui.Theme()
    normal_texture = arcade.Texture('normal')
    clicked_texture = arcade.Texture('clicked')
    theme.button_textures['normal'] = normal_texture
    theme.button_textures['clicked'] = clicked_texture
    button = TextButton(center_x=50, center_y=20, width=30, height=10, text='',
                        theme=theme)

    button.pressed = False
    button.draw_texture_theme()
    arcade.draw_texture_rectangle.assert_called_once_with(50, 20, 30, 10,
                                                          normal_texture)

    arcade.draw_texture_rectangle.reset_mock()
    button.pressed = True
    button.draw_texture_theme()
    arcade.draw_texture_rectangle.assert_called_once_with(50, 20, 30, 10,
                                                          clicked_texture)


def test_draw_color_theme(mocker):
    mocker.patch('arcade.draw_rectangle_filled')
    mocker.patch('arcade.draw_line')

    button = TextButton(center_x=50, center_y=20, width=30, height=10, text='')

    button.pressed = False
    button.draw_color_theme()
    arcade.draw_rectangle_filled.assert_called_once_with(50, 20, 30, 10,
                                                         button.face_color)

    assert arcade.draw_line.call_count == 4
    assert arcade.draw_line.call_args_list == [
        call(
            button.get_left(), button.get_bottom(),
            button.get_right(), button.get_bottom(),
            button.shadow_color, button.button_height
        ),
        call(
            button.get_right(), button.get_bottom(),
            button.get_right(), button.get_top(),
            button.shadow_color, button.button_height
        ),
        call(
            button.get_left(), button.get_top(),
            button.get_right(), button.get_top(),
            button.highlight_color, button.button_height
        ),
        call(
            button.get_left(), button.get_bottom(),
            button.get_left(), button.get_top(),
            button.highlight_color, button.button_height
        )
    ]

    arcade.draw_rectangle_filled.reset_mock()
    arcade.draw_line.reset_mock()
    button.pressed = True
    button.draw_color_theme()
    arcade.draw_rectangle_filled.assert_called_once_with(50, 20, 30, 10,
                                                         button.face_color)

    assert arcade.draw_line.call_count == 4
    assert arcade.draw_line.call_args_list == [
        call(
            button.get_left(), button.get_bottom(),
            button.get_right(), button.get_bottom(),
            button.highlight_color, button.button_height
        ),
        call(
            button.get_right(), button.get_bottom(),
            button.get_right(), button.get_top(),
            button.highlight_color, button.button_height
        ),
        call(
            button.get_left(), button.get_top(),
            button.get_right(), button.get_top(),
            button.shadow_color, button.button_height
        ),
        call(
            button.get_left(), button.get_bottom(),
            button.get_left(), button.get_top(),
            button.shadow_color, button.button_height
        )
    ]
