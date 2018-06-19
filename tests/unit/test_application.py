

def test_import(mock_window):
    assert 'Window' == mock_window.__name__


def test_constructs(mock_window):
    w = mock_window()
    assert 'Window' == w.__class__.__name__


def test_initializes_defaults(mocker, mock_window):
    mocker.patch.object(mock_window, 'set_update_rate')
    w = mock_window()
    assert 600 == w.height
    assert 800 == w.width
    assert 'Arcade Window' == w.caption
    assert False is w._fullscreen
    assert False is w.resizable
    w.set_update_rate.assert_called_once_with(1 / 60)
    assert False is w.invalid


def test_update(mock_window):
    w = mock_window()
    assert None is w.on_update(1.1111)


def test_set_update_rate_constructor(mock_window, pyglet_clock):
    w = mock_window()
    pyglet_clock.unschedule.assert_called_with(w.on_update)
    pyglet_clock.schedule_interval.assert_called_with(w.on_update, 1 / 60)


def test_set_update_rate(mock_window, pyglet_clock):
    w = mock_window()
    w.set_update_rate(1 / 2)
    pyglet_clock.unschedule.assert_called_with(w.on_update, )
    pyglet_clock.schedule_interval.assert_called_with(w.on_update, 0.5)


def test_on_mouse_motion(mock_window):
    w = mock_window()
    assert None is w.on_mouse_motion(0, 0, 0, 0)


def test_on_mouse_press(mock_window):
    w = mock_window()
    assert None is w.on_mouse_press(0, 0, 0, 0)


def test_on_mouse_drag(mock_window, mocker):
    w = mock_window()
    mocker.patch.object(w, 'on_mouse_motion')
    assert None is w.on_mouse_drag(0, 0, 0, 0, 0, 0)
    w.on_mouse_motion.assert_called_once_with(0, 0, 0, 0)


def test_on_mouse_release(mock_window):
    w = mock_window()
    assert None is w.on_mouse_release(0, 0, 0, 0)


def test_on_mouse_scroll(mock_window):
    w = mock_window()
    assert None is w.on_mouse_scroll(0, 0, 0, 0)
