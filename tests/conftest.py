import pytest
import arcade


def pytest_addoption(parser):
    parser.addoption("--twm", action="store_true", default=False, help="Disable window geometry tests when using a tiling window manager" )


@pytest.fixture(scope="function")
def twm(pytestconfig):
    if pytestconfig.getoption("twm"):
        return True
    return False


@pytest.fixture(scope="function")
def ctx():
    window = arcade.Window(800, 600, "Test")
    try:
        window.clear()
        yield window.ctx
    finally:
        window.close()


@pytest.fixture(scope="function")
def window():
    window = arcade.Window(800, 600, "Test")
    try:
        window.clear()
        yield window
    finally:
        window.close()
