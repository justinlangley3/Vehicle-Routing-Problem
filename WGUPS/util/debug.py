from enum import Enum, auto
from types import FrameType

index_err = 'Msg=\'Index out of range\''
key_value_err = 'Msg=\'Key cannot be a negative value\''
lookup_err = 'Msg=\'Object was not found\''
type_err = 'Msg=\'Objects are not of the same type\''
value_err = 'Msg=\'Value is out of the allowed range\''

#
#   Note: This whole file needs gutted and proper logging put in place
#         It had a short-term purpose which has been long-fulfilled
#

def debug_msg(error: Enum, frame: FrameType) -> str:
    """
    Provides a specified debug message from the provided stack frame
    :param error: Enum(Error): Located in this module
    :param frame: a stack frame object
    :return: str
    """
    module_name = frame.f_globals['__name__']
    class_name = frame.f_locals['self'].__class__.__name__
    function_name = frame.f_code.co_name

    msg = f'\n\tModule={repr(module_name)},' \
          f' Class={repr(class_name)},' \
          f' Func={repr(function_name)}:\n\t\t'

    if error.value == Error.INDEX.VALUE:
        msg += index_err
    if error.value == Error.KEY_VALUE.VALUE:
        msg += key_value_err
    if error.value == Error.LOOKUP.VALUE:
        msg += lookup_err
    if error.value == Error.TYPE.VALUE:
        msg += type_err
    if error.value == Error.VALUE.VALUE:
        msg += value_err

    return msg


class Error(Enum):
    INDEX = auto()
    KEY_VALUE = auto()
    LOOKUP = auto()
    TYPE = auto()
    VALUE = auto()
