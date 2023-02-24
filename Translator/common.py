def is_whitespace(ch: str) -> bool:
    return ch == ' ' or ch == '\n' or ch == '\t'


def is_eof(ch: str) -> bool:
    return ch == ''


def get_escape_sequences(ch: str) -> str:
    if ch == 'a':
        return '\a'
    elif ch == 'b':
        return '\b'
    elif ch == 'f':
        return '\f'
    elif ch == 'n':
        return '\n'
    elif ch == 'r':
        return '\r'
    elif ch == 't':
        return '\t'
    elif ch == 'v':
        return '\v'
    elif ch == "'":
        return "\'"
    elif ch == '"':
        return '\"'
    elif ch == '\\':
        return '\\'
    else:
        raise ValueError("No such escape sequence")