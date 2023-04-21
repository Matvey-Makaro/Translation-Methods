from tables import *
from common import *


class LexicalAnalyzerError(Exception):
    def __init__(self, text: str, fname: str, line_num: int, ch_num: int):
        self._txt = 'Lexical analyzer:' + 'File "' + fname + '", line ' + str(line_num) + ' col ' + str(ch_num) + ': ' + text
        super().__init__(self._txt)


class LexicalAnalyzer:
    def __init__(self, fname: str, literal_table: LiteralTable, variable_table: list):
        self._fname = fname

        try:
            self._file = open(self._fname, 'r')
        except FileNotFoundError as er:
            print(er)
            exit(-1)

        self._ch = ''
        self._buffer = ''
        self._state = States.START
        self._lexemes = []
        self._literal_table = literal_table
        self._variable_table = variable_table
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
            self._add_lexem(LexemTypes.KEY_WORD, key_words[self._buffer])
        else:
            id = self._add_to_variable_table(self._buffer)
            self._add_lexem(LexemTypes.IDENTIFIER, id)

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

        if not is_whitespace(self._ch) and self._ch not in operators and not self._ch == ';' and not is_eof(self._ch) \
                and self._ch != ')' and self._ch != ']':
            self._error_description = "wrong characters after a number"
            self._state = States.ERROR
            return

        if was_dot:
            literal_type = LiteralTypes.DOUBLE_CONSTANT
            lexem_type = LexemTypes.DOUBLE_NUM
        else:
            literal_type = LiteralTypes.INT_CONSTANT
            lexem_type = LexemTypes.INT_NUM

        id = self._add_to_literal_table(self._buffer, literal_type)
        self._add_lexem(lexem_type, id)

        self._state = States.START

    def _delimiter_state(self) -> None:
        self._add_lexem(LexemTypes.DELIMITER, delimiters[self._ch])
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

        id = self._add_to_literal_table(self._buffer, LiteralTypes.STRING_CONSTANT)
        self._add_lexem(LexemTypes.STRING, id)
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

            self._add_lexem(LexemTypes.OPERATOR, operators[self._buffer])
            self._readch()
            self._state = States.START
            return

        if is_operator(first_symbol):
            self._add_lexem(LexemTypes.OPERATOR, operators[first_symbol])
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

    def _add_lexem(self, type: LexemTypes, value) -> None:
        if type == LexemTypes.IDENTIFIER or type == LexemTypes.STRING or \
                type == LexemTypes.INT_NUM or type == LexemTypes.DOUBLE_NUM:
            col_num = self._ch_num - len(self._buffer)
        else:
            col_num = self._ch_num  # TODO: There may be an error here.

        # Removed because value is no longer a string, but an enumeration.
        # else:
        #     col_num = self._ch_num - len(value)

        self._lexemes.append(LexTableItem(type, value, self._line_num + 1, col_num + 1))

    def _add_to_literal_table(self, value: str, type: LiteralTypes) -> int:
        return self._literal_table.push(value, type)

    def _add_to_variable_table(self, name: str) -> int:
        # TODO: Can be replaced by a faster search using a hash table.
        for i in range(len(self._variable_table)):
            if self._variable_table[i].name == name:
                return i

        self._variable_table.append(VariableTableItem(name, VariableTypes.UNKNOWN, -1, -1))
        return len(self._variable_table) - 1

    def get_lexemes(self) -> list:
        return self._lexemes
