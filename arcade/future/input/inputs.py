"""
Enums used to map different input types to their common counterparts.

For example, keyboard keys are mapped to their Pyglet int values, as are mouse buttons.
However Controller buttons and axes are mapped to their Pyglet string values.
"""

from enum import Enum, auto
from sys import platform

from arcade.future.input.raw_dicts import RawBindBase


class InputType(Enum):
    KEYBOARD = 0
    MOUSE_BUTTON = 1
    MOUSE_AXIS = 2
    CONTROLLER_BUTTON = 3
    CONTROLLER_AXIS = 4


class InputEnum(Enum):
    """The base class for all input value :py:class:`enum.Enum` types."""

    pass


class StrEnum(str, InputEnum):
    def __new__(cls, value, *args, **kwargs):
        if not isinstance(value, str | auto):
            raise TypeError(f"Values of StrEnums must be strings: {value!r} is a {type(value)}")
        return super().__new__(cls, value, *args, **kwargs)

    def __str__(self):
        return str(self.value)

    @staticmethod
    def _generate_next_value_(name, *_):
        return name


class ControllerAxes(StrEnum):
    LEFT_STICK_X = "leftx"
    LEFT_STICK_POSITIVE_X = "leftxpositive"
    LEFT_STICK_NEGATIVE_X = "leftxnegative"
    LEFT_STICK_Y = "lefty"
    LEFT_STICK_POSITIVE_Y = "leftypositive"
    LEFT_STICK_NEGATIVE_Y = "leftynegative"
    RIGHT_STICK_X = "rightx"
    RIGHT_STICK_POSITIVE_X = "rightxpositive"
    RIGHT_STICK_NEGATIVE_X = "rightxnegative"
    RIGHT_STICK_Y = "righty"
    RIGHT_STICK_POSITIVE_Y = "rightypositive"
    RIGHT_STICK_NEGATIVE_Y = "rightynegative"
    LEFT_TRIGGER = "lefttrigger"
    RIGHT_TRIGGER = "righttrigger"


class ControllerButtons(StrEnum):
    TOP_FACE = "y"
    RIGHT_FACE = "b"
    LEFT_FACE = "x"
    BOTTOM_FACE = "a"
    LEFT_SHOULDER = "leftshoulder"
    RIGHT_SHOULDER = "rightshoulder"
    LEFT_TRIGGER = "lefttrigger"
    RIGHT_TRIGGER = "righttrigger"
    START = "start"
    BACK = "back"
    GUIDE = "guide"
    LEFT_STICK = "leftstick"
    RIGHT_STICK = "rightstick"
    DPAD_LEFT = "dpleft"
    DPAD_RIGHT = "dpright"
    DPAD_UP = "dpup"
    DPAD_DOWN = "dpdown"


class XBoxControllerButtons(StrEnum):
    Y = ControllerButtons.TOP_FACE
    B = ControllerButtons.RIGHT_FACE
    X = ControllerButtons.LEFT_FACE
    A = ControllerButtons.BOTTOM_FACE
    LEFT_BUMPER = ControllerButtons.LEFT_SHOULDER
    RIGHT_BUMPER = ControllerButtons.RIGHT_SHOULDER
    START = ControllerButtons.START
    SELECT = ControllerButtons.BACK
    GUIDE = ControllerButtons.GUIDE
    LEFT_STICK = ControllerButtons.LEFT_STICK
    RIGHT_STICK = ControllerButtons.RIGHT_STICK
    DPAD_LEFT = ControllerButtons.DPAD_LEFT
    DPAD_RIGHT = ControllerButtons.DPAD_RIGHT
    DPAD_UP = ControllerButtons.DPAD_UP
    DPAD_DOWN = ControllerButtons.DPAD_DOWN


class PSControllerButtons(StrEnum):
    TRIANGLE = ControllerButtons.TOP_FACE
    CIRCLE = ControllerButtons.RIGHT_FACE
    SQUARE = ControllerButtons.LEFT_FACE
    CROSS = ControllerButtons.BOTTOM_FACE
    L1 = ControllerButtons.LEFT_SHOULDER
    R1 = ControllerButtons.RIGHT_SHOULDER
    L2 = ControllerButtons.LEFT_TRIGGER
    R2 = ControllerButtons.RIGHT_TRIGGER
    L3 = ControllerButtons.LEFT_STICK
    R3 = ControllerButtons.RIGHT_STICK
    START = ControllerButtons.START
    SELECT = ControllerButtons.BACK
    GUIDE = ControllerButtons.GUIDE
    DPAD_LEFT = ControllerButtons.DPAD_LEFT
    DPAD_RIGHT = ControllerButtons.DPAD_RIGHT
    DPAD_UP = ControllerButtons.DPAD_UP
    DPAD_DOWN = ControllerButtons.DPAD_DOWN


class Keys(InputEnum):
    # Key modifiers
    # Done in powers of two, so you can do a bit-wise 'and' to detect
    # multiple modifiers.
    MOD_SHIFT = 1
    MOD_CTRL = 2
    MOD_ALT = 4
    MOD_CAPSLOCK = 8
    MOD_NUMLOCK = 16
    MOD_WINDOWS = 32
    MOD_COMMAND = 64
    MOD_OPTION = 128
    MOD_SCROLLLOCK = 256

    # Platform-specific base hotkey modifier
    MOD_ACCEL = MOD_COMMAND if platform == "darwin" else MOD_CTRL

    # Keys
    BACKSPACE = 65288
    TAB = 65289
    LINEFEED = 65290
    CLEAR = 65291
    RETURN = 65293
    ENTER = 65293
    PAUSE = 65299
    SCROLLLOCK = 65300
    SYSREQ = 65301
    ESCAPE = 65307
    HOME = 65360
    LEFT = 65361
    UP = 65362
    RIGHT = 65363
    DOWN = 65364
    PAGEUP = 65365
    PAGEDOWN = 65366
    END = 65367
    BEGIN = 65368
    DELETE = 65535
    SELECT = 65376
    PRINT = 65377
    EXECUTE = 65378
    INSERT = 65379
    UNDO = 65381
    REDO = 65382
    MENU = 65383
    FIND = 65384
    CANCEL = 65385
    HELP = 65386
    BREAK = 65387
    MODESWITCH = 65406
    SCRIPTSWITCH = 65406
    MOTION_UP = 65362
    MOTION_RIGHT = 65363
    MOTION_DOWN = 65364
    MOTION_LEFT = 65361
    MOTION_NEXT_WORD = 1
    MOTION_PREVIOUS_WORD = 2
    MOTION_BEGINNING_OF_LINE = 3
    MOTION_END_OF_LINE = 4
    MOTION_NEXT_PAGE = 65366
    MOTION_PREVIOUS_PAGE = 65365
    MOTION_BEGINNING_OF_FILE = 5
    MOTION_END_OF_FILE = 6
    MOTION_BACKSPACE = 65288
    MOTION_DELETE = 65535
    NUMLOCK = 65407
    NUM_SPACE = 65408
    NUM_TAB = 65417
    NUM_ENTER = 65421
    NUM_F1 = 65425
    NUM_F2 = 65426
    NUM_F3 = 65427
    NUM_F4 = 65428
    NUM_HOME = 65429
    NUM_LEFT = 65430
    NUM_UP = 65431
    NUM_RIGHT = 65432
    NUM_DOWN = 65433
    NUM_PRIOR = 65434
    NUM_PAGE_UP = 65434
    NUM_NEXT = 65435
    NUM_PAGE_DOWN = 65435
    NUM_END = 65436
    NUM_BEGIN = 65437
    NUM_INSERT = 65438
    NUM_DELETE = 65439
    NUM_EQUAL = 65469
    NUM_MULTIPLY = 65450
    NUM_ADD = 65451
    NUM_SEPARATOR = 65452
    NUM_SUBTRACT = 65453
    NUM_DECIMAL = 65454
    NUM_DIVIDE = 65455

    # Numbers on the numberpad
    NUM_0 = 65456
    NUM_1 = 65457
    NUM_2 = 65458
    NUM_3 = 65459
    NUM_4 = 65460
    NUM_5 = 65461
    NUM_6 = 65462
    NUM_7 = 65463
    NUM_8 = 65464
    NUM_9 = 65465

    F1 = 65470
    F2 = 65471
    F3 = 65472
    F4 = 65473
    F5 = 65474
    F6 = 65475
    F7 = 65476
    F8 = 65477
    F9 = 65478
    F10 = 65479
    F11 = 65480
    F12 = 65481
    F13 = 65482
    F14 = 65483
    F15 = 65484
    F16 = 65485
    F17 = 65486
    F18 = 65487
    F19 = 65488
    F20 = 65489
    F21 = 65490
    F22 = 65491
    F23 = 65492
    F24 = 65493
    LSHIFT = 65505
    RSHIFT = 65506
    LCTRL = 65507
    RCTRL = 65508
    CAPSLOCK = 65509
    LMETA = 65511
    RMETA = 65512
    LALT = 65513
    RALT = 65514
    LWINDOWS = 65515
    RWINDOWS = 65516
    LCOMMAND = 65517
    RCOMMAND = 65518
    LOPTION = 65488
    ROPTION = 65489
    SPACE = 32
    EXCLAMATION = 33
    DOUBLEQUOTE = 34
    HASH = 35
    POUND = 35
    DOLLAR = 36
    PERCENT = 37
    AMPERSAND = 38
    APOSTROPHE = 39
    PARENLEFT = 40
    PARENRIGHT = 41
    ASTERISK = 42
    PLUS = 43
    COMMA = 44
    MINUS = 45
    PERIOD = 46
    SLASH = 47

    # Numbers on the main keyboard
    KEY_0 = 48
    KEY_1 = 49
    KEY_2 = 50
    KEY_3 = 51
    KEY_4 = 52
    KEY_5 = 53
    KEY_6 = 54
    KEY_7 = 55
    KEY_8 = 56
    KEY_9 = 57
    COLON = 58
    SEMICOLON = 59
    LESS = 60
    EQUAL = 61
    GREATER = 62
    QUESTION = 63
    AT = 64
    BRACKETLEFT = 91
    BACKSLASH = 92
    BRACKETRIGHT = 93
    ASCIICIRCUM = 94
    UNDERSCORE = 95
    GRAVE = 96
    QUOTELEFT = 96
    A = 97
    B = 98
    C = 99
    D = 100
    E = 101
    F = 102
    G = 103
    H = 104
    I = 105
    J = 106
    K = 107
    L = 108
    M = 109
    N = 110
    O = 111
    P = 112
    Q = 113
    R = 114
    S = 115
    T = 116
    U = 117
    V = 118
    W = 119
    X = 120
    Y = 121
    Z = 122
    BRACELEFT = 123
    BAR = 124
    BRACERIGHT = 125
    ASCIITILDE = 126


class MouseAxes(InputEnum):
    X = 0
    Y = 1


class MouseButtons(InputEnum):
    # LEFT and MOUSE_1 are aliases of each other
    LEFT = 1 << 0
    MOUSE_1 = 1 << 0

    # MIDDLE and MOUSE_3 are aliases of each other
    MIDDLE = 1 << 1
    MOUSE_3 = 1 << 1

    # RIGHT and MOUSE_2 are aliases of each other
    RIGHT = 1 << 2
    MOUSE_2 = 1 << 2

    MOUSE_4 = 1 << 3
    MOUSE_5 = 1 << 4


# This improves on if ladders since:
# 1. Enum types with members are final
# 2. Types are hashable
# It may be worth encapsulating this approach since we have other if
# ladders without case-specific logic remaining in the controller code.
CLASS_TO_INPUT_TYPE: dict[type[InputEnum], InputType] = {
    Keys: InputType.KEYBOARD,
    MouseButtons: InputType.MOUSE_BUTTON,
    MouseAxes: InputType.MOUSE_AXIS,
    ControllerButtons: InputType.CONTROLLER_BUTTON,
    ControllerAxes: InputType.CONTROLLER_AXIS,
}

INPUT_TYPE_TO_CLASS: dict[InputType, type[InputEnum]] = {
    InputType.KEYBOARD: Keys,
    InputType.MOUSE_BUTTON: MouseButtons,
    InputType.MOUSE_AXIS: MouseAxes,
    InputType.CONTROLLER_BUTTON: ControllerButtons,
    InputType.CONTROLLER_AXIS: ControllerAxes,
}


def parse_mapping_input_enum(raw: "RawBindBase") -> InputEnum:
    """Parse the :py:class:`InputEnum` for a given raw value.

    See :py:class:`.RawBindBase` to learn more about required arguments.

    Args:
        raw:
            A dict with ``"input_type"`` and ``"input"`` corresponding
            to :py:class:`InputEnum` values.

    Returns:
        An :py:class:`InputEnum`.
    """
    _raw_input = raw["input"]
    _input_type = InputType(raw["input_type"])

    _input_class = INPUT_TYPE_TO_CLASS.get(_input_type, None)
    if _input_class is None:
        raise AttributeError(f"Tried to parse an unknown input type {_input_type}")

    return _input_class(_raw_input)
