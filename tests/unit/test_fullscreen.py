import time


def test_fullscreen(window):
    time.sleep(0.1)

    window.set_fullscreen(True)
    window.flip()

    time.sleep(0.1)

    window.set_fullscreen(False)
    window.flip()
