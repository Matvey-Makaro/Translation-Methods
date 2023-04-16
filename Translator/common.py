from dataclasses import dataclass
from enum import Enum


class KeyWords(Enum):
    INT = 0,
    DOUBLE = 1,
    BOOL = 2,
    STRING = 3,
    VOID = 4,
    TRUE = 5,
    FALSE = 6,
    NULLPTR = 7,
    WHILE = 8,
    CONTINUE = 9,
    BREAK = 10,
    IF = 11,
    ELSE = 12,
    PRINT = 13,
    SCAN = 14,
    TO_STRING = 15,
    STOI = 16,
    STOD = 17,
    EXIT = 18,


class Delimiters(Enum):
    OPEN_PARENTHESIS = 0,
    CLOSE_PARENTHESIS = 1,
    SEMICOLON = 2,
    OPEN_BRACES = 3,
    CLOSE_BRACES = 4,
    OPEN_SQUARE_BRACKET = 5,
    CLOSE_SQUARE_BRACKET = 6


class Operators(Enum):
    EQUAL = 0,
    NOT = 1,
    NOT_EQUAL = 2,
    AND = 3,
    OR = 4,
    PLUS = 5,
    MINUS = 6,
    ASTERISK = 7,
    SLASH = 8,
    DOUBLE_SLASH = 9,
    LESS = 10,
    GREATER = 11,
    LESS_OR_EQUAL = 12,
    GREATER_OR_EQUAL = 13,
    PERCENT = 14,
    DOUBLE_EQUAL = 15,
    AMPERSAND = 16


class States(Enum):
    START = 0,
    ID_OR_KEY_WORD = 1,
    NUMBER = 2,
    DELIMITER = 3,
    OPERATOR = 4,
    STRING = 5,
    ONE_LINE_COMMENT = 6,
    ERROR = 9,
    END = 10,


class LexemTypes(Enum):
    KEY_WORD = 0,
    IDENTIFIER = 1,
    DELIMITER = 2,
    OPERATOR = 3,
    INT_NUM = 4,
    DOUBLE_NUM = 5,
    STRING = 6


key_words = {
    'int': KeyWords.INT,
    'double': KeyWords.DOUBLE,
    'bool': KeyWords.BOOL,
    'string': KeyWords.STRING,
    'void': KeyWords.VOID,
    'true': KeyWords.TRUE,
    'false': KeyWords.FALSE,
    'nullptr': KeyWords.NULLPTR,
    'while': KeyWords.WHILE,
    'continue': KeyWords.CONTINUE,
    'break': KeyWords.BREAK,
    'if': KeyWords.IF,
    'else': KeyWords.ELSE,
    'print': KeyWords.PRINT,
    'scan': KeyWords.SCAN,
    'to_string': KeyWords.TO_STRING,
    'stoi': KeyWords.STOI,
    'stod': KeyWords.STOD,
    'exit': KeyWords.EXIT
}

delimiters = {
    '(': Delimiters.OPEN_PARENTHESIS,
    ')': Delimiters.CLOSE_PARENTHESIS,
    ';': Delimiters.SEMICOLON,
    '{': Delimiters.OPEN_BRACES,
    '}': Delimiters.CLOSE_BRACES,
    '[': Delimiters.OPEN_SQUARE_BRACKET,
    ']': Delimiters.CLOSE_SQUARE_BRACKET
}

operators = {
    '=': Operators.EQUAL,
    '!': Operators.NOT,
    '==': Operators.DOUBLE_EQUAL,
    '!=': Operators.NOT_EQUAL,
    '<': Operators.LESS,
    '<=': Operators.LESS_OR_EQUAL,
    '>': Operators.GREATER,
    '>=': Operators.GREATER_OR_EQUAL,
    '&&': Operators.AND,
    '||': Operators.OR,
    '+': Operators.PLUS,
    '-': Operators.MINUS,
    '*': Operators.ASTERISK,
    '/': Operators.SLASH,
    '%': Operators.PERCENT,
    '//': Operators.DOUBLE_SLASH,
    '&': Operators.AMPERSAND
}


@dataclass()
class LexTableItem:
    type: LexemTypes
    value: int or KeyWords or Delimiters or Operators
    line_num: int
    col_num: int


class LiteralTypes(Enum):
    INT_CONSTANT = 1,
    DOUBLE_CONSTANT = 2,
    STRING_CONSTANT = 3,


class VariableTypes(Enum):
    UNKNOWN = 0,
    INT = 1,
    DOUBLE = 2,
    STRING = 3,
    BOOL = 4


def is_key_word(word: str) -> bool:
    return word in key_words


def is_delimiter(s: str) -> bool:
    return s in delimiters


def is_operator(s: str) -> bool:
    return s in operators


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
