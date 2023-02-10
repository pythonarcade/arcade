"""
Various utility functions.

IMPORTANT:
These  should be standalone and not rely on any arcade imports
"""
import platform
import sys
from typing import Tuple
from pathlib import Path
from io import StringIO


def generate_uuid_from_kwargs(**kwargs) -> str:
    """
    Given key/pair combos, returns a string in uuid format.
    Such as `text='hi', size=32` it will return "text-hi-size-32".
    Called with no parameters, id does NOT return a random unique id.
    """
    if len(kwargs) == 0:
        raise Exception("generate_uuid_from_kwargs has to be used with kwargs, please check the doc.")

    with StringIO() as guid:
        for key, value in kwargs.items():
            guid.write(str(key))
            guid.write(str(value))
            guid.write("-")
        return guid.getvalue()


def is_raspberry_pi() -> bool:
    """
    Determine if the host is a rasberry pi.

    :returns: bool
    """
    return get_raspberry_pi_info()[0]


def get_raspberry_pi_info() -> Tuple[bool, str, str]:
    """
    Determine if the host is a raspberry pi
    with additional info.

    :returns: 3 component tuple.
              bool (is host a raspi)
              str (architechture)
              str (model name)
    """
    # armv7l is raspi 32 bit
    # aarch64 is raspi 64 bit
    architecture = platform.machine()
    model_name = ""

    # The platform for raspi should always be linux
    if not sys.platform == "linux":
        return False, 0, ""

    # Check for model info file
    MODEL_PATH = Path("/sys/firmware/devicetree/base/model")
    if MODEL_PATH.exists():
        try:
            model_name = MODEL_PATH.read_text()[:-1]
            if "raspberry pi" in model_name.lower():
                return True, architecture, model_name
        except Exception:
            pass

    return False, "", ""
