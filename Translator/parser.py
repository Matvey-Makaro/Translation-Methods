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


class UsingBeforeDeclarationError(ParserError):
    def __init__(self, var_name: str, fname: str, line_num: int, ch_num: int):
        super().__init__(f"Varible {var_name} using before declaration", fname, line_num, ch_num)


class DoubleDeclarationError(ParserError):
    def __init__(self, var_name: str, fname: str, line_num: int, ch_num: int):
        super().__init__(f"Double declaration of variable {var_name}", fname, line_num, ch_num)


class Node:
    def __init__(self, lexem):
        self._lexem = lexem
        self._childs = []

    def add_child(self, node) -> None:
        self._childs.append(node)

    def get_lexem(self) -> LexTableItem:
        return self._lexem


class Parser:
    def __init__(self, fname: str, lexemes: list, literal_table: LiteralTable, variable_table: list):
        self._fname = fname
        self._lexemes = lexemes
        self._literal_table = literal_table
        self._variable_table = variable_table
        self._curr_lex_index = 0
        self._block_level = 0
        self._block_id = 0
        self._scope_stack = [(self._block_level, self._block_id)]
        self.parse()

    def _go_to_next_lexeme(self) -> None:
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

    def _expect_var_type(self, lexeme: LexTableItem, type: VariableTypes) -> None:
        if lexeme.type != LexemTypes.IDENTIFIER:
            raise ExpectedError(str(type) + "variable expected", self._fname, lexeme.line_num, lexeme.col_num)
        var = self._get_variable(lexeme)
        if var.type != type:
            raise ExpectedError(str(type) + "variable expected", self._fname, lexeme.line_num, lexeme.col_num)

    def _are_lexemes_remaining(self) -> bool:
        return self._curr_lex_index < len(self._lexemes)

    def _get_curr_lexeme(self) -> LexTableItem:
        return self._lexemes[self._curr_lex_index]

    def _get_variable(self, lexeme: LexTableItem) -> VariableTableItem:
        return self._variable_table[lexeme.value]

    def _enter_block(self) -> None:
        self._block_level += 1
        self._block_id += 1
        self._scope_stack.append((self._block_level, self._block_id))

    def _exit_block(self) -> None:
        self._block_level -= 1
        self._scope_stack.pop()

    def _parse_block_code(self):
        self._expect_delimiter(Delimiters.OPEN_BRACES)
        self._enter_block()

        self._exit_block()

    def _parse_declare_identifier(self, var_type: VariableTypes) -> Node:
        lexeme = self._get_curr_lexeme()
        node = Node(lexeme)
        curr_var = self._get_variable(lexeme)

        block_level = self._scope_stack[-1][0]
        block_id = self._scope_stack[-1][1]

        if curr_var.type != VariableTypes.UNKNOWN:
            for var in self._variable_table:
                if curr_var.name == var.name and curr_var.block_id == var.block_id:
                    raise DoubleDeclarationError(curr_var.name, self._fname, lexeme.line_num, lexeme.col_num)

            self._variable_table.append(VariableTableItem(curr_var.name, var_type, block_level, block_id))
            lexeme.value = len(self._variable_table) - 1

        curr_var.type = var_type
        curr_var.block_level = block_level
        curr_var.block_id = block_id

        self._go_to_next_lexeme()
        return node

    def _parse_using_identifier(self) -> Node:
        lexeme = self._get_curr_lexeme()
        node = Node(lexeme)

        var = self._get_variable(lexeme)
        if var.type == VariableTypes.UNKNOWN:
            raise UsingBeforeDeclarationError(var.name, self._fname, lexeme.line_num, lexeme.col_num)

        var_real_id = -1
        for scope in reversed(self._scope_stack):
            block_level = scope[0]
            block_id = scope[1]
            searched_var = VariableTableItem(var.name, var.type, block_level, block_id)

            try:
                var_real_id = self._variable_table.index(searched_var)
                break
            except ValueError:
                pass

        if var_real_id < 0:
            raise UsingBeforeDeclarationError(var.name, self._fname, lexeme.line_num, lexeme.col_num)

        lexeme.value = var_real_id
        self._go_to_next_lexeme()
        return node

    def _parse_to_string(self) -> Node:
        self._expect_key_word(KeyWords.TO_STRING)
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.OPEN_PARENTHESIS)
        self._go_to_next_lexeme()
        # TODO: parse arithmetic, bool or string expression.
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.CLOSE_PARENTHESIS)
        self._go_to_next_lexeme()

    def _parse_string_terminal(self) -> Node:
        lexeme = self._get_curr_lexeme()
        if lexeme.type == LexemTypes.IDENTIFIER:
            node = self._parse_using_identifier()
            self._expect_var_type(node.get_lexem(), VariableTypes.STRING)
        elif lexeme.value == KeyWords.TO_STRING:
            node = self._parse_to_string()

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
                elif lexeme.value == Delimiters.OPEN_BRACES:
                    self._parse_block_code()

            self._go_to_next_lexeme()  # TODO: Delete later.
