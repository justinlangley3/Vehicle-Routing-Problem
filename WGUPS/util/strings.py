import re


def str_to_chars(string: str) -> list[str]:
    return [char for char in string]


def padr(string: str, count: int, pad_char: str = ' ') -> str:
    return string + (pad_char * count)


def tokenize(string: str, sep: str = ' '):
    return string.split(sep=sep)


def find_token(string: str, key: str) -> str | None:
    """
    Extracts a token from a string.
    We can think of a token as "key=value"

    A token may also include a delimiter.
    Spaces should be ignored for characters between a pair of delimiters

    Args:
        string: a string to search
        key: a string containing the token key

    Returns: str, the token found

    """
    if string is None:
        return None

    pattern = re.compile(r"\b(\w+)=(.*?)(?=\s\w+=\s*|$)")
    tokens = re.split(pattern=pattern, string=string)
    if key in tokens:
        return '='.join(tokens)[1:-1]
    return None


def unpack_token(token: str, delimited: bool = False) -> str:
    token = token.split(sep='=').pop()
    if delimited:
        return token[1:-1]
    else:
        return token
