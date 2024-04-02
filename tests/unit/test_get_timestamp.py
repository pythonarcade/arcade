"""Minimal tests for arcade.get_timestamp.

Since the function is a minimal fallback for people who can't use any of
the alternatives to  :py:mod:`datetime`, we'll only check the following:

* Local system time on the test machine
* A made-up time zone guaranteed not to clash with it
* Two built-ins which implement strftime-like behavior:

  * :py:class:`datetime.date`
  * :py:class:`datetime.time`

It's not our responsibility to check 3rd party date & time types for
compatibility. Instead, we cover it in doc and advise users to choose
one of the popular backward-compatible date & time replacements.

"""
import datetime

from arcade import get_timestamp

import time_machine
from dateutil.tz import tzlocal, tzoffset


# System time zone + a zone guaranteed not to clash with it
LOCAL_TZ = tzlocal()
CUSTOM_TZ = tzoffset(
    'arcade',
    datetime.timedelta(hours=-5, minutes=4, seconds=3))

# Set up date and time constants to use with strfime checks
DATE = datetime.date(
    year=2024,
    month=12,
    day=11)

TIME = datetime.time(
    hour=10,
    minute=9,
    second=8,
    microsecond=7)

DATETIME_NOW = datetime.datetime.combine(DATE, TIME, tzinfo=LOCAL_TZ)
DATETIME_NOW_CUSTOM = datetime.datetime.combine(DATE, TIME, tzinfo=CUSTOM_TZ)


def test_get_timestamp() -> None:

   # Check default usage and all flags individually w/o combinations
    with time_machine.travel (DATETIME_NOW, tick=False):
        assert get_timestamp() == '2024_12_11_1009_08_000007'
        assert get_timestamp(how="%Y") == '2024'
        assert get_timestamp(how="%m") == '12'
        assert get_timestamp(how="%d") == '11'
        assert get_timestamp(how="%H") == "10"
        assert get_timestamp(how="%M") == "09"
        assert get_timestamp(how="%S") == "08"
        assert get_timestamp(how="%f") == "000007"

    # Make sure passing time zones works the same way as above
    with time_machine.travel(DATETIME_NOW_CUSTOM, tick=False):
        assert get_timestamp(tzinfo=CUSTOM_TZ) == '2024_12_11_1009_08_000007'
        assert get_timestamp(how="%Y", tzinfo=CUSTOM_TZ) == '2024'
        assert get_timestamp(how="%m", tzinfo=CUSTOM_TZ) == '12'
        assert get_timestamp(how="%d", tzinfo=CUSTOM_TZ) == '11'
        assert get_timestamp(how="%H", tzinfo=CUSTOM_TZ) == "10"
        assert get_timestamp(how="%M", tzinfo=CUSTOM_TZ) == "09"
        assert get_timestamp(how="%S", tzinfo=CUSTOM_TZ) == "08"
        assert get_timestamp(how="%f", tzinfo=CUSTOM_TZ) == "000007"

    # Spot-check two other built-in strftime-providing objects
    assert get_timestamp(how="%Y-%m-%d", when=DATE) == "2024-12-11"
    assert get_timestamp(how="%Y", when=DATE) == '2024'
    assert get_timestamp(how="%m", when=DATE) == '12'
    assert get_timestamp(how="%d", when=DATE) == '11'

    assert get_timestamp(how="%H:%M:%S.%f", when=TIME) == "10:09:08.000007"
    assert get_timestamp(how="%H", when=TIME) == "10"
    assert get_timestamp(how="%M", when=TIME) == "09"
    assert get_timestamp(how="%S", when=TIME) == "08"
    assert get_timestamp(how="%f", when=TIME) == "000007"
