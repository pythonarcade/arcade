import pytest
import arcade

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600


def create_window():
    return arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, "Testing")


def pytest_addoption(parser):
    parser.addoption("--twm", action="store_true", default=False, help="Disable window geometry tests when using a tiling window manager" )


@pytest.fixture(scope="function")
def twm(pytestconfig):
    if pytestconfig.getoption("twm"):
        return True
    return False


@pytest.fixture(scope="function")
def ctx():
    window = create_window()
    try:
        yield window.ctx
    finally:
        window.close()


@pytest.fixture(scope="function")
def window():
    window = create_window()
    try:
        yield window
    finally:
        window.close()
