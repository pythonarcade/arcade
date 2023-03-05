"""
Unit tests for utils.py

Can run these tests individually with:
python -m pytest tests/unit/test_utils.py
"""
from arcade import utils


def test_generate_uuid_from_kwargs():
    value = utils.generate_uuid_from_kwargs(text="hi", size=32)
    assert value == "text=hi|size=32"


def test_is_raspberry_pi():
    assert isinstance(utils.is_raspberry_pi(), bool)


def test_get_raspberry_pi_info():
    is_raspi, arch, model = utils.get_raspberry_pi_info()
    assert isinstance(is_raspi, bool)
    assert isinstance(arch, str)
    assert isinstance(model, str)
