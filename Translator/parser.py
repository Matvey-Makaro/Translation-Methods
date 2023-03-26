from lexical_analyzer import *


def is_variable_type(key_word: KeyWords) -> bool:
    return key_word == KeyWords.INT or key_words == KeyWords.DOUBLE or \
        key_word == KeyWords.BOOL or key_word == KeyWords.STRING or key_word == KeyWords.VOID


class ParserError(Exception):
    def __init__(self, text: str, fname: str, line_num: int, ch_num: int):
        self._txt = 'File "' + fname + '", line ' + str(line_num) + ' col ' + str(ch_num) + ': ' + text
        super().__init__(self._txt)


class ExpectedError(ParserError):
    def __init__(self, expected: str, fname: str, line_num: int, ch_num: int):
        super().__init__(f"{expected} expected", fname, line_num, ch_num)


class Node:
    def __init__(self, lexem):
        self._lexem = lexem
        self._childs = []

    def add_child(self, node) -> None:
        self._childs.append(node)


class Parser:
    def __init__(self, fname: str, lexemes: list, literal_table: LiteralTable, variable_table: list):
        self._fname = fname
        self._lexemes = lexemes
        self._literal_table = literal_table
        self._variable_table = variable_table
        self._curr_lex_index = 0
        self._block_level = 0
        self._block_id = 0
        self.parse()

    def _go_to_next_lexeme(self) -> LexTableItem:
        self._curr_lex_index += 1

    def _is_match_cur_lexeme(self, type) -> bool:
        if type == LexemTypes.IDENTIFIER or type == LexemTypes.INT_NUM or \
                type == LexemTypes.DOUBLE_NUM or type == LexemTypes.STRING:
            return type == self._lexemes[self._curr_lex_index].type
        else:
            return type == self._lexemes[self._curr_lex_index].value

    def _expect_key_word(self, key_word: KeyWords) -> None:
        lexeme = self._get_curr_lexeme()
        if lexeme.value != key_word:
            raise ExpectedError(str(key_word), self._fname, lexeme.line_num, lexeme.col_num)

    def _expect_delimiter(self, delimiter: Delimiters) -> None:
        lexeme = self._get_curr_lexeme()
        if lexeme.value != delimiter:
            raise ExpectedError(str(delimiter), self._fname, lexeme.line_num, lexeme.col_num)

    def _expect_operator(self, operator: Operators) -> None:
        lexeme = self._get_curr_lexeme()
        if lexeme.value != operator:
            raise ExpectedError(str(operator), self._fname, lexeme.line_num, lexeme.col_num)

    def _are_lexemes_remaining(self):
        return self._curr_lex_index < len(self._lexemes)

    def _get_curr_lexeme(self) -> LexTableItem:
        return self._lexemes[self._curr_lex_index]

    def _parse_string_teriminal(self):
        lexeme = self._get_curr_lexeme()
        if lexeme.type == LexemTypes.IDENTIFIER:
            pass

    def _parse_string_expression(self):
        pass

    def _parse_print(self) -> Node:
        self._expect_key_word(KeyWords.PRINT)
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.OPEN_PARENTHESIS)
        self._go_to_next_lexeme()
        # TODO: parse string here
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.CLOSE_PARENTHESIS)
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.SEMICOLON)
        self._go_to_next_lexeme()

    def _parse_type(self):
        pass

    def parse(self):
        while self._are_lexemes_remaining():
            lexeme = self._get_curr_lexeme()
            if lexeme.type == LexemTypes.KEY_WORD:
                if lexeme.value == KeyWords.PRINT:
                    self._parse_print()
                elif is_variable_type(lexeme.value):
                    pass
            self._go_to_next_lexeme()  # TODO: Delete later.
