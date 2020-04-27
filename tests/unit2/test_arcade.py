import logging
import arcade


def test_logging():
    arcade.configure_logging(logging.WARNING)
    logger = logging.getLogger('arcade')
    assert logger.level == logging.WARNING
