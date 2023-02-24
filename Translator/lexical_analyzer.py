from enum import Enum
from dataclasses import dataclass
from common import *

key_words = frozenset({
    'int',
    'double',
    'bool',
    'string',
    'void',
    'true',
    'false',
    'nullptr',
    'while',
    'continue',
    'break',
    'if',
    'else',
    'print',
    'scan',
    'to_string',
    'stoi',
    'stod',
    'exit'
})

delimiters = frozenset({
    '(',
    ')',
    ';',
    '{',
    '}'
})

operators = frozenset({
    '=',
    '!',
    '!=',
    '&&',
    '||',
    '+',
    '-',
    '*',
    '/',
    '//'
})


def is_key_word(word: str) -> bool:
    return word in key_words


def is_delimiter(s: str) -> bool:
    return s in delimiters


def is_operator(s: str) -> bool:
    return s in operators


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


class Operators(Enum):
    EQUAL = 0,
    NOT = 1,
    NOT_EQUAL = 2,
    AND = 3,
    OR = 4,
    ADD = 5,
    SUB = 6,
    MUL = 7,
    DIV = 8,
    DOUBLE_SLASH = 9


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


@dataclass()
class LexTableItem:
    type: LexemTypes
    value: str


class NameTableItemTypes(Enum):
    VARIABLE = 0,
    INT_CONSTANT = 1,
    DOUBLE_CONSTANT = 2,
    STRING_CONSTANT = 3,


@dataclass()
class NameTableItem:
    type: NameTableItemTypes
    id: int


class NameTable:
    def __init__(self):
        self._name_table = {}
        self._id_counter = 0

    def push(self, name: str, type: NameTableItemTypes) -> int:
        if name in self._name_table:
            return self._name_table.get(name).id

        id = self._id_counter
        self._id_counter += 1
        self._name_table[name] = NameTableItem(type, id)
        return id


class LexicalAnalyzerError(Exception):
    def __init__(self, text: str, fname: str, line_num: int, ch_num: int):
        self._txt = 'File "' + fname + '", line ' + str(line_num) + ' col ' + str(ch_num) + ': ' + text

    def __str__(self):
        return self._txt


class LexicalAnalyzer:
    def __init__(self, fname: str, name_table: NameTable):
        self._fname = fname
        self._file = open(self._fname, 'r')
        self._ch = ''
        self._buffer = ''
        self._state = States.START
        self._lexemes = []
        self._name_table = name_table
        self._line_num = 0
        self._ch_num = 0
        self._error_description = ''
        self.analyze()

    def analyze(self) -> None:
        self._readch()
        while True:
            if self._state == States.START:
                self._start_state()
            elif self._state == States.ID_OR_KEY_WORD:
                self._id_or_key_word_state()
            elif self._state == States.NUMBER:
                self._number_state()
            elif self._state == States.DELIMITER:
                self._delimiter_state()
            elif self._state == States.OPERATOR:
                self._operator_state()
            elif self._state == States.STRING:
                self._string_state()
            elif self._state == States.ONE_LINE_COMMENT:
                self._one_line_comment_state()
            elif self._state == States.ERROR:
                self._error_state()
            elif self._state == States.END:
                return

    def _start_state(self) -> None:
        while is_whitespace(self._ch):
            self._readch()

        if self._ch.isalpha() or self._ch == '_':
            self._state = States.ID_OR_KEY_WORD
        elif self._ch.isdigit() or self._ch == '.':
            self._state = States.NUMBER
        elif is_delimiter(self._ch):
            self._state = States.DELIMITER
        elif self._ch == '"':
            self._state = States.STRING
        elif is_eof(self._ch):
            self._state = States.END
        else:
            self._state = States.OPERATOR

    def _id_or_key_word_state(self) -> None:
        self._buffer = ''
        while self._ch.isalnum() or self._ch == '_':
            self._buffer += self._ch
            self._readch()

        if is_key_word(self._buffer):
            self._add_lexem(LexemTypes.KEY_WORD, self._buffer)
        else:
            id = self._add_to_name_table(self._buffer, NameTableItemTypes.VARIABLE)
            self._add_lexem(LexemTypes.IDENTIFIER, str(id))

        self._state = States.START

    def _number_state(self) -> None:
        self._buffer = ''
        was_dot = False
        while self._ch.isdigit() or self._ch == '.':
            if self._ch == '.':
                if was_dot:
                    self._error_description = 'too many decimal points in number'
                    self._state = States.ERROR
                    return
                was_dot = True
            self._buffer += self._ch
            self._readch()

        if not is_whitespace(self._ch) and self._ch not in operators and not self._ch == ';' and not is_eof(self._ch):
            self._error_description = "wrong characters after a number"
            self._state = States.ERROR
            return

        if was_dot:
            name_table_item_type = NameTableItemTypes.DOUBLE_CONSTANT
            lexem_type = LexemTypes.DOUBLE_NUM
        else:
            name_table_item_type = NameTableItemTypes.INT_CONSTANT
            lexem_type = LexemTypes.INT_NUM

        id = self._add_to_name_table(self._buffer, name_table_item_type)
        self._add_lexem(lexem_type, str(id))

        self._state = States.START

    def _delimiter_state(self) -> None:
        self._add_lexem(LexemTypes.DELIMITER, self._ch)
        self._readch()
        self._state = States.START

    def _string_state(self) -> None:
        self._buffer = ''
        self._readch()
        while self._ch != '"':
            if self._ch == '\n' or is_eof(self._ch):
                self._error_description = 'missing terminating " character'
                self._state = States.ERROR
                return

            if self._ch == '\\':
                self._readch()
                try:
                    self._buffer += get_escape_sequences(self._ch)
                except ValueError:
                    self._error_description = 'no such escape sequence'
                    # -1 because we read 2 characters, and an error should be issued for the first one
                    self._ch_num -= 1
                    self._state = States.ERROR
                    return
            else:
                self._buffer += self._ch

            self._readch()

        id = self._add_to_name_table(self._buffer, NameTableItemTypes.STRING_CONSTANT)
        self._add_lexem(LexemTypes.STRING, str(id))
        self._readch()
        self._state = States.START

    def _operator_state(self) -> None:
        self._buffer = ''
        first_symbol = self._ch
        self._buffer += self._ch
        self._readch()
        self._buffer += self._ch

        if is_operator(self._buffer):
            if self._buffer == '//':
                self._state = States.ONE_LINE_COMMENT
                self._readch()
                return

            self._add_lexem(LexemTypes.OPERATOR, self._buffer)
            self._readch()
            self._state = States.START
            return

        if is_operator(first_symbol):
            self._add_lexem(LexemTypes.OPERATOR, first_symbol)
            self._state = States.START
            return

        self._error_description = "unknown character"
        # -1 because we read 2 characters, and an error should be issued for the first one
        self._ch_num -= 1
        self._state = States.ERROR

    def _one_line_comment_state(self) -> None:
        while not (self._ch == '\n' or is_eof(self._ch)):
            self._readch()
        self._state = States.START

    def _error_state(self) -> None:
        raise LexicalAnalyzerError(self._error_description, self._fname, self._line_num + 1, self._ch_num + 1)

    def _readch(self) -> None:
        if self._ch == '\n':
            self._line_num += 1
            self._ch_num = 0
        else:
            self._ch_num += 1
        self._ch = self._file.read(1)

    def _add_lexem(self, type: LexemTypes, value: str) -> None:
        self._lexemes.append(LexTableItem(type, value))

    def _add_to_name_table(self, name: str, type: NameTableItemTypes) -> int:
        return self._name_table.push(name, type)

    def get_lexemes(self) -> list:
        return self._lexemes
