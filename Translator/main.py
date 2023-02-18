from enum import Enum
from dataclasses import dataclass

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
    ';'
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


def is_delimeter(s: str) -> bool:
    return s in delimiters


def is_operator(s: str) -> bool:
    return s in operators


def is_whitespace(ch: str) -> bool:
    return ch == ' ' or ch == '\n' or ch == '\t'


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


def get_words(line: str) -> list:
    line = line.replace('(', ' ( ')
    line = line.replace(')', ' ) ')
    line = line.replace(';', ' ; ')
    line = line.replace(';', ' ; ')
    return line.split()


class States(Enum):
    START = 0,
    ID_OR_KEY_WORD = 1,
    NUMBER = 2,
    DELIMITER = 3,
    ERROR_STATE = 9,
    END_STATE = 10,


class LexemTypes(Enum):
    KEY_WORD = 0,
    IDENTIFIER = 1,
    DELIMITERS = 2,
    OPERATORS = 3


@dataclass()
class LexTableItem:
    type: LexemTypes
    value: int


class NameTableItemTypes(Enum):
    VARIABLE = 0,
    CONSTANT = 1,


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


class LexicalAnalyzer:
    def __init__(self, f, name_table: NameTable):
        self.file = f
        self.ch = ''
        self.buffer = ''
        self.int_num = 0
        self.state = States.START
        self.lexemes = []
        self._name_table = name_table
        self.analyze()

    def analyze(self):
        self.ch = self.file.read(1)
        while self.ch != '':
            print(self.ch, end='')

            if self.state == States.START:
                self.start_state()
            elif self.state == States.ID_OR_KEY_WORD:
                self.id_or_key_word_state()
            elif self.state == States.NUMBER:
                self.number_state()

    def start_state(self):
        if is_whitespace(self.ch):
            self.ch = self.file.read(1)
            return
        elif self.ch.isalpha():
            self.buffer = ''
            self.buffer += self.ch
            self.state = States.ID_OR_KEY_WORD
        elif self.ch.isdigit():
            self.int_num += ord(self.ch) - ord('0')
            self.state = States.NUMBER
        else:
            # TODO: Убрать это
            print("Unreachable!")
            exit()

    def id_or_key_word_state(self) -> None:
        self.ch = self.file.read(1)
        while self.ch.isalnum():
            self.buffer += self.ch
            self.ch = self.file.read(1)

        if is_key_word(self.buffer):
            self.lexemes.append(LexTableItem(LexemTypes.KEY_WORD, self.buffer))
        else:
            id = self._name_table.push(self.buffer, NameTableItemTypes.VARIABLE)
            self.lexemes.append(LexTableItem(LexemTypes.IDENTIFIER, str(id)))

        self.state = States.START

    def number_state(self):
        pass


def main() -> None:
    # fname = input("Enter file name: ")
    fname = "test.cpp"
    name_table = NameTable()
    with open(fname, 'r') as f:
        lex_analyzer = LexicalAnalyzer(f, name_table)

    delete_later = 0


if __name__ == '__main__':
    main()
