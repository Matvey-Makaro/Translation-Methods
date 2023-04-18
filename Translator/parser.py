from common import *
from tables import *


def is_variable_type(key_word: KeyWords) -> bool:
    return key_word == KeyWords.INT or key_word == KeyWords.DOUBLE or \
        key_word == KeyWords.BOOL or key_word == KeyWords.STRING or key_word == KeyWords.VOID


def is_addop(op: Operators) -> bool:
    return op == Operators.PLUS or op == Operators.MINUS


def is_mulop(op: Operators) -> bool:
    return op in (Operators.ASTERISK, Operators.SLASH, Operators.PERCENT)


class ExpressionTypes(Enum):
    ARITHMETIC = 0,
    BOOL = 1,
    STRING = 2


class ComparisonTypes(Enum):
    ARITHMETIC = 0,
    STRING = 1


class ParserError(Exception):
    def __init__(self, text: str, fname: str, line_num: int, ch_num: int):
        self._txt = 'File "' + fname + '", line ' + str(line_num) + ' col ' + str(ch_num) + ': ' + text
        super().__init__(self._txt)


class ExpectedError(ParserError):
    def __init__(self, expected: str, fname: str, line_num: int, ch_num: int):
        super().__init__(f"{expected} expected.", fname, line_num, ch_num)


class UsingBeforeDeclarationError(ParserError):
    def __init__(self, var_name: str, fname: str, line_num: int, ch_num: int):
        super().__init__(f"Varible {var_name} using before declaration.", fname, line_num, ch_num)


class DoubleDeclarationError(ParserError):
    def __init__(self, var_name: str, fname: str, line_num: int, ch_num: int):
        super().__init__(f"Double declaration of variable {var_name}.", fname, line_num, ch_num)


class NotSubscriptable(ParserError):
    def __init__(self, var_name: str, fname: str, line_num: int, ch_num: int):
        super().__init__(f"Variable {var_name} is not subscriptable.", fname, line_num, ch_num)


def print_tree(root, depth: int = 0):
    if root is None:
        return

    print('\t' * depth + str(root))
    for child in root.get_childs():
        print_tree(child, depth + 1)


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
        self._root = Node(None, NodeTypes.CODE_BLOCK)
        self._nesting_while = 0
        self.parse()

    def print_syntax_tree(self) -> None:
        print_tree(self._root)

    def get_tree(self) -> Node:
        return self._root

    def _is_break_available(self) -> bool:
        return self._nesting_while > 0

    def _is_continue_available(self) -> bool:
        return self._nesting_while > 0

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

    def _expect_var_type(self, lexeme: LexTableItem, type: VariableTypes or tuple) -> None:
        if lexeme.type != LexemTypes.IDENTIFIER:
            raise ExpectedError(str(type) + " variable", self._fname, lexeme.line_num, lexeme.col_num)
        var = self._get_variable(lexeme)
        if isinstance(type, VariableTypes):
            if var.type != type:
                raise ExpectedError(str(type) + " variable", self._fname, lexeme.line_num, lexeme.col_num)
        else:
            if var.type not in type:
                raise ExpectedError("One of the following variable types: " + str(type), self._fname,
                                    lexeme.line_num, lexeme.col_num)

    def _expect_identifier(self) -> None:
        lexeme = self._get_curr_lexeme()
        if lexeme.type != LexemTypes.IDENTIFIER:
            raise ExpectedError("identifier", self._fname, lexeme.line_num, lexeme.col_num)

    def _expect_stoid(self) -> None:
        lexeme = self._get_curr_lexeme()
        if not (lexeme.value in (KeyWords.STOI, KeyWords.STOD)):
            raise ExpectedError("stoi or stod", self._fname, lexeme.line_num, lexeme.col_num)

    def _expect_comparison_operator(self) -> None:
        lexeme = self._get_curr_lexeme()
        if not (lexeme.value in (Operators.DOUBLE_EQUAL, Operators.NOT_EQUAL, Operators.LESS,
                                 Operators.LESS_OR_EQUAL, Operators.GREATER, Operators.GREATER_OR_EQUAL)):
            raise ExpectedError("One of the comparison operators", self._fname, lexeme.line_num, lexeme.col_num)

    def _expect_bool_literal(self) -> None:
        lexeme = self._get_curr_lexeme()
        if lexeme.value != KeyWords.TRUE and lexeme.value != KeyWords.FALSE:
            raise ExpectedError("Bool literal", self._fname, lexeme.line_num, lexeme.col_num)

    def _expect_string_literal(self) -> None:
        lexeme = self._get_curr_lexeme()
        if lexeme.type != LexemTypes.STRING:
            raise ExpectedError("String literal", self._fname, lexeme.line_num, lexeme.col_num)

    def _expect_int_literal(self) -> None:
        lexeme = self._get_curr_lexeme()
        if lexeme.type != LexemTypes.INT_NUM:
            raise ExpectedError("Int literal", self._fname, lexeme.line_num, lexeme.col_num)

    def _are_lexemes_remaining(self) -> bool:
        return self._curr_lex_index < len(self._lexemes)

    def _get_curr_lexeme(self) -> LexTableItem:
        if not self._are_lexemes_remaining():
            lexeme = self._lexemes[self._curr_lex_index - 1]
            raise ParserError("Unexpected end of file", self._fname, lexeme.col_num, lexeme.col_num)
        return self._lexemes[self._curr_lex_index]

    def _get_variable(self, lexeme: LexTableItem) -> VariableTableItem:
        return self._variable_table[lexeme.value]

    def _get_literal(self, lexeme: LexTableItem) -> LiteralTableItem:
        return self._literal_table.get(lexeme.value)

    def _enter_block(self) -> None:
        self._block_level += 1
        self._block_id += 1
        self._scope_stack.append((self._block_level, self._block_id))

    def _exit_block(self) -> None:
        self._block_level -= 1
        self._scope_stack.pop()

    def _parse_block_code(self) -> Node:
        self._expect_delimiter(Delimiters.OPEN_BRACES)
        self._go_to_next_lexeme()
        self._enter_block()

        code_block_node = Node(None, NodeTypes.CODE_BLOCK)

        while self._are_lexemes_remaining() and not self._is_match_cur_lexeme(Delimiters.CLOSE_BRACES):
            code_block_node.add_child(self._parse_statement())

        self._expect_delimiter(Delimiters.CLOSE_BRACES)
        self._go_to_next_lexeme()
        self._exit_block()

        return code_block_node

    def _parse_optional_array(self, identifier_node: Node) -> Node:
        if not self._are_lexemes_remaining() or not self._is_match_cur_lexeme(Delimiters.OPEN_SQUARE_BRACKET):
            return identifier_node

        self._go_to_next_lexeme()
        self._expect_int_literal()
        identifier_lexeme = identifier_node.get_lexeme()
        identifier_var = self._get_variable(identifier_lexeme)
        arr_size = self._get_literal(self._get_curr_lexeme()).value
        identifier_var.is_array = True
        identifier_var.array_size = arr_size
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.CLOSE_SQUARE_BRACKET)
        self._go_to_next_lexeme()
        return identifier_node

    def _parse_declare_identifier(self, var_type: VariableTypes) -> Node:
        self._expect_identifier()
        lexeme = self._get_curr_lexeme()
        node = Node(lexeme)
        curr_var = self._get_variable(lexeme)

        block_level = self._scope_stack[-1][0]
        block_id = self._scope_stack[-1][1]

        if curr_var.type != VariableTypes.UNKNOWN:
            for var in self._variable_table:
                if curr_var.name == var.name and block_id == var.block_id:
                    raise DoubleDeclarationError(curr_var.name, self._fname, lexeme.line_num, lexeme.col_num)

            self._variable_table.append(VariableTableItem(curr_var.name, var_type, block_level, block_id))
            curr_var = self._variable_table[-1]
            lexeme.value = len(self._variable_table) - 1

        curr_var.type = var_type
        curr_var.block_level = block_level
        curr_var.block_id = block_id

        self._go_to_next_lexeme()

        node = self._parse_optional_array(node)

        return node

    def _parse_using_identifier(self) -> Node:
        self._expect_identifier()
        lexeme = self._get_curr_lexeme()
        var = self._get_variable(lexeme)

        if var.type == VariableTypes.UNKNOWN:
            raise UsingBeforeDeclarationError(var.name, self._fname, lexeme.line_num, lexeme.col_num)

        var_real_id = -1
        was_found = False
        for scope in reversed(self._scope_stack):
            if was_found:
                break
            block_level = scope[0]
            block_id = scope[1]
            searched_var = VariableTableItem(var.name, var.type, block_level, block_id)
            for i in range(len(self._variable_table)):
                variable = self._variable_table[i]
                if variable.name == var.name and variable.type == variable.type and \
                        variable.block_level == block_level and variable.block_id == block_id:
                    var_real_id = i
                    was_found = True
                    break

        if var_real_id < 0:
            raise UsingBeforeDeclarationError(var.name, self._fname, lexeme.line_num, lexeme.col_num)

        lexeme.value = var_real_id
        self._go_to_next_lexeme()

        if self._is_match_cur_lexeme(Delimiters.OPEN_SQUARE_BRACKET):
            if not var.is_array:
                raise NotSubscriptable(var.name, self._fname, lexeme.line_num, lexeme.col_num)

            self._go_to_next_lexeme()
            node = Node(lexeme, NodeTypes.INDEX_APPEAL)
            node.add_child(Node(lexeme))
            node.add_child(self._parse_arithmetic_expression())
            self._expect_delimiter(Delimiters.CLOSE_SQUARE_BRACKET)
            self._go_to_next_lexeme()
        else:
            node = Node(lexeme)

        return node

    def _parse_operator(self, op: Operators):
        self._expect_operator(op)
        op_node = Node(self._get_curr_lexeme())
        self._go_to_next_lexeme()
        return op_node

    def _parse_stoid(self) -> Node:
        self._expect_stoid()
        lexeme = self._get_curr_lexeme()
        stoid_node = Node(lexeme)
        self._go_to_next_lexeme()

        self._expect_delimiter(Delimiters.OPEN_PARENTHESIS)
        self._go_to_next_lexeme()
        string_node = self._parse_string_expression()
        self._expect_delimiter(Delimiters.CLOSE_PARENTHESIS)
        self._go_to_next_lexeme()

        stoid_node.add_child(string_node)
        return stoid_node

    def _parse_terminal(self) -> Node:
        lexeme = self._get_curr_lexeme()

        if self._is_match_cur_lexeme(Delimiters.OPEN_PARENTHESIS):
            self._go_to_next_lexeme()
            node = self._parse_arithmetic_expression()
            self._expect_delimiter(Delimiters.CLOSE_PARENTHESIS)
            self._go_to_next_lexeme()
        elif lexeme.type in (LexemTypes.INT_NUM, LexemTypes.DOUBLE_NUM):
            node = Node(lexeme)
            self._go_to_next_lexeme()
        elif lexeme.value in (KeyWords.STOI, KeyWords.STOD):
            node = self._parse_stoid()
        elif lexeme.type == LexemTypes.IDENTIFIER:
            node = self._parse_using_identifier()
            self._expect_var_type(node.get_lexeme(), (VariableTypes.INT, VariableTypes.DOUBLE))
        else:
            raise ExpectedError("Number", self._fname, lexeme.line_num, lexeme.col_num)

        return node

    def _parse_terminals_and_mul_ops(self) -> Node:
        lhs_node = self._parse_terminal()

        while self._are_lexemes_remaining() and is_mulop(self._get_curr_lexeme().value):
            lexeme = self._get_curr_lexeme()
            op_node = self._parse_operator(lexeme.value)
            rhs_node = self._parse_terminal()
            op_node.add_child(lhs_node)
            op_node.add_child(rhs_node)
            lhs_node = op_node

        return lhs_node

    def _parse_unary_operation_and_terminal(self) -> Node:
        lexeme = self._get_curr_lexeme()
        op_node = None
        if is_addop(lexeme.value):
            op_node = self._parse_operator(lexeme.value)

        node = self._parse_terminals_and_mul_ops()

        if op_node is None:
            return node

        op_node.add_child(node)
        return op_node

    def _parse_arithmetic_expression(self) -> Node:
        lhs_node = self._parse_unary_operation_and_terminal()

        while self._are_lexemes_remaining() and is_addop(self._get_curr_lexeme().value):
            lexeme = self._get_curr_lexeme()
            op_node = self._parse_operator(lexeme.value)
            rhs_node = self._parse_terminals_and_mul_ops()
            op_node.add_child(lhs_node)
            op_node.add_child(rhs_node)
            lhs_node = op_node

        return lhs_node

    def _parse_bool_literal(self) -> Node:
        self._expect_bool_literal()
        node = Node(self._get_curr_lexeme())
        self._go_to_next_lexeme()
        return node

    def _parse_comparison_term(self) -> (Node, ComparisonTypes):
        lexeme = self._get_curr_lexeme()
        old_lex_index = self._curr_lex_index

        try:
            node = self._parse_arithmetic_expression()
            return node, ComparisonTypes.ARITHMETIC
        except ExpectedError:
            self._curr_lex_index = old_lex_index
            try:
                node = self._parse_string_expression()
                return node, ComparisonTypes.STRING
            except ExpectedError:
                raise ExpectedError("arithmetic or string expression", self._fname, lexeme.line_num, lexeme.col_num)

    def _parse_comparison(self) -> Node:
        lexeme = self._get_curr_lexeme()
        lhs_node, lhs_type = self._parse_comparison_term()
        self._expect_comparison_operator()
        op_node = Node(self._get_curr_lexeme())
        self._go_to_next_lexeme()
        rhs_node, rhs_type = self._parse_comparison_term()

        if lhs_type != rhs_type:
            raise ParserError("Can't compare " + str(lhs_type) + " and " + str(rhs_type),
                              self._fname, lexeme.line_num, lexeme.col_num)

        op_node.add_child(lhs_node)
        op_node.add_child(rhs_node)
        return op_node

    def _parse_bool_term(self) -> Node:
        lexeme = self._get_curr_lexeme()
        if lexeme.type == LexemTypes.IDENTIFIER and self._get_variable(lexeme).type == VariableTypes.BOOL:
            node = self._parse_using_identifier()
        elif self._is_match_cur_lexeme(Delimiters.OPEN_PARENTHESIS):
            old_lex_index = self._curr_lex_index
            self._go_to_next_lexeme()

            # Can be bool experession or a comparison.
            try:
                node = self._parse_bool_expression()
                self._expect_delimiter(Delimiters.CLOSE_PARENTHESIS)
                self._go_to_next_lexeme()
            except ParserError:
                self._curr_lex_index = old_lex_index
                node = self._parse_comparison()
        elif lexeme.value in (KeyWords.TRUE, KeyWords.FALSE):
            node = self._parse_bool_literal()
        else:
            node = self._parse_comparison()

        return node

    def _parse_bool_term_with_possible_not(self) -> Node:
        was_not = False
        not_node = None
        if self._is_match_cur_lexeme(Operators.NOT):
            not_node = self._parse_operator(Operators.NOT)
            was_not = True

        node = self._parse_bool_term()
        if not was_not:
            return node

        not_node.add_child(node)
        return not_node

    def _parse_bool_and(self) -> Node:
        lhs_node = self._parse_bool_term_with_possible_not()

        while self._are_lexemes_remaining() and self._is_match_cur_lexeme(Operators.AND):
            and_node = self._parse_operator(Operators.AND)
            rhs_node = self._parse_bool_term_with_possible_not()
            and_node.add_child(lhs_node)
            and_node.add_child(rhs_node)
            lhs_node = and_node

        return lhs_node

    def _parse_bool_expression(self) -> Node:
        lhs_node = self._parse_bool_and()

        while self._are_lexemes_remaining() and self._is_match_cur_lexeme(Operators.OR):
            or_node = self._parse_operator(Operators.OR)
            rhs_node = self._parse_bool_and()
            or_node.add_child(lhs_node)
            or_node.add_child((rhs_node))
            lhs_node = or_node

        return lhs_node

    def _parse_to_string(self) -> Node:
        self._expect_key_word(KeyWords.TO_STRING)
        to_string_node = Node(self._get_curr_lexeme())
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.OPEN_PARENTHESIS)
        self._go_to_next_lexeme()
        # TODO: Add bool_expression.
        expr_node = self._parse_arithmetic_expression()
        self._expect_delimiter(Delimiters.CLOSE_PARENTHESIS)
        self._go_to_next_lexeme()
        to_string_node.add_child(expr_node)
        return to_string_node

    def _parse_scan(self) -> Node:
        self._expect_key_word(KeyWords.SCAN)
        scan_node = Node(self._get_curr_lexeme())
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.OPEN_PARENTHESIS)
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.CLOSE_PARENTHESIS)
        self._go_to_next_lexeme()
        return scan_node

    def _parse_string_terminal(self) -> Node:
        lexeme = self._get_curr_lexeme()
        if lexeme.type == LexemTypes.IDENTIFIER:
            node = self._parse_using_identifier()
            self._expect_var_type(node.get_lexeme(), VariableTypes.STRING)
        elif lexeme.value == KeyWords.TO_STRING:
            node = self._parse_to_string()
        elif lexeme.value == KeyWords.SCAN:
            node = self._parse_scan()
        else:
            self._expect_string_literal()
            node = Node(lexeme)
            self._go_to_next_lexeme()

        return node

    def _parse_string_expression(self):
        lhs_node = self._parse_string_terminal()

        while self._are_lexemes_remaining() and self._is_match_cur_lexeme(Operators.PLUS):
            op_node = self._parse_operator(Operators.PLUS)
            rhs_node = self._parse_string_terminal()
            op_node.add_child(lhs_node)
            op_node.add_child(rhs_node)
            lhs_node = op_node

        return lhs_node

    def _parse_print(self) -> Node:
        self._expect_key_word(KeyWords.PRINT)
        print_node = Node(self._get_curr_lexeme())
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.OPEN_PARENTHESIS)
        self._go_to_next_lexeme()
        string_expr_node = self._parse_string_expression()
        self._expect_delimiter(Delimiters.CLOSE_PARENTHESIS)
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.SEMICOLON)
        self._go_to_next_lexeme()
        print_node.add_child(string_expr_node)
        return print_node

    def _parse_var_type(self) -> (Node, VariableTypes):
        type_lexeme = self._get_curr_lexeme()
        type_node = Node(type_lexeme)
        var_type = VariableTypes.UNKNOWN
        if type_lexeme.value == KeyWords.INT:
            var_type = VariableTypes.INT
        elif type_lexeme.value == KeyWords.DOUBLE:
            var_type = VariableTypes.DOUBLE
        elif type_lexeme.value == KeyWords.STRING:
            var_type = VariableTypes.STRING
        elif type_lexeme.value == KeyWords.BOOL:
            var_type = VariableTypes.BOOL
        else:
            raise ParserError("Unknown variable type", self._fname, type_lexeme.line_num, type_lexeme.col_num)

        self._go_to_next_lexeme()
        return type_node, var_type

    def _parse_assignment(self, identifier_node: Node) -> Node:
        self._expect_operator(Operators.EQUAL)
        equal_lexeme = self._get_curr_lexeme()
        equal_node = Node(equal_lexeme)
        equal_node.add_child(identifier_node)
        self._go_to_next_lexeme()

        identifier_lexeme = identifier_node.get_lexeme()
        var = self._get_variable(identifier_lexeme)
        var_type = var.type

        if var_type in (VariableTypes.INT, VariableTypes.DOUBLE):
            rhs_node = self._parse_arithmetic_expression()
        elif var_type == VariableTypes.STRING:
            rhs_node = self._parse_string_expression()
        elif var_type == VariableTypes.BOOL:
            rhs_node = self._parse_bool_expression()
        else:
            ParserError("Unknown type of identifier.", self._fname,
                        identifier_lexeme.line_num, identifier_lexeme.col_num)

        equal_node.add_child(rhs_node)
        return equal_node

    def _parse_optional_initialization(self, identifier_node: Node) -> Node:
        if not self._are_lexemes_remaining() or not self._is_match_cur_lexeme(Operators.EQUAL):
            return identifier_node
        return self._parse_assignment(identifier_node)

    def _parse_var_declaration(self) -> Node:
        type_node, var_type = self._parse_var_type()
        identifier_node = self._parse_declare_identifier(var_type)
        declaration_node = Node(None, NodeTypes.DECLARATION)
        declaration_node.add_child(type_node)
        ident_or_eq_node = self._parse_optional_initialization(identifier_node)
        declaration_node.add_child(ident_or_eq_node)
        self._expect_delimiter(Delimiters.SEMICOLON)
        self._go_to_next_lexeme()
        return declaration_node

    def _parse_if(self) -> Node:
        self._expect_key_word(KeyWords.IF)
        if_node = Node(self._get_curr_lexeme())
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.OPEN_PARENTHESIS)
        self._go_to_next_lexeme()
        if self._is_match_cur_lexeme(Delimiters.CLOSE_PARENTHESIS):
            lexeme = self._get_curr_lexeme()
            raise ExpectedError("Bool expression", self._fname, lexeme.line_num, lexeme.col_num)
        condition_node = self._parse_bool_expression()
        self._expect_delimiter(Delimiters.CLOSE_PARENTHESIS)
        self._go_to_next_lexeme()
        if_statement_node = self._parse_statement()
        if_node.add_child(condition_node)
        if_node.add_child(if_statement_node)

        if self._are_lexemes_remaining() and self._is_match_cur_lexeme(KeyWords.ELSE):
            self._go_to_next_lexeme()
            else_statement_node = self._parse_statement()
            if_node.add_child(else_statement_node)

        return if_node

    def _parse_while(self) -> Node:
        self._expect_key_word(KeyWords.WHILE)
        while_node = Node(self._get_curr_lexeme())
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.OPEN_PARENTHESIS)
        self._go_to_next_lexeme()
        if self._is_match_cur_lexeme(Delimiters.CLOSE_PARENTHESIS):
            lexeme = self._get_curr_lexeme()
            raise ExpectedError("Bool expression", self._fname, lexeme.line_num, lexeme.col_num)
        condition_node = self._parse_bool_expression()
        while_node.add_child(condition_node)
        self._expect_delimiter(Delimiters.CLOSE_PARENTHESIS)
        self._go_to_next_lexeme()
        if self._is_match_cur_lexeme(Delimiters.SEMICOLON):
            return while_node

        self._nesting_while += 1
        statement_node = self._parse_statement()
        self._nesting_while -= 1
        while_node.add_child(statement_node)
        return while_node

    def _parse_exit(self) -> Node:
        self._expect_key_word(KeyWords.EXIT)
        exit_node = Node(self._get_curr_lexeme())
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.OPEN_PARENTHESIS)
        self._go_to_next_lexeme()
        exit_code_node = self._parse_arithmetic_expression()
        self._expect_delimiter(Delimiters.CLOSE_PARENTHESIS)
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.SEMICOLON)
        self._go_to_next_lexeme()

        exit_node.add_child(exit_code_node)
        return exit_node

    def _parse_break(self) -> Node:
        lexeme = self._get_curr_lexeme()
        if not self._is_break_available():
            raise ParserError("break is not available in this context.", self._fname, lexeme.line_num, lexeme.col_num)
        self._expect_key_word(KeyWords.BREAK)
        node = Node(lexeme)
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.SEMICOLON)
        self._go_to_next_lexeme()
        return node

    def _parse_continue(self) -> Node:
        lexeme = self._get_curr_lexeme()
        if not self._is_continue_available():
            raise ParserError("continue is not available in this context.", self._fname, lexeme.line_num,
                              lexeme.col_num)
        self._expect_key_word(KeyWords.CONTINUE)
        node = Node(lexeme)
        self._go_to_next_lexeme()
        self._expect_delimiter(Delimiters.SEMICOLON)
        self._go_to_next_lexeme()
        return node

    def _parse_statement(self) -> Node:
        lexeme = self._get_curr_lexeme()
        if lexeme.type == LexemTypes.KEY_WORD:
            if lexeme.value == KeyWords.PRINT:
                return self._parse_print()
            elif is_variable_type(lexeme.value):
                return self._parse_var_declaration()
            elif lexeme.value == KeyWords.IF:
                return self._parse_if()
            elif lexeme.value == KeyWords.WHILE:
                return self._parse_while()
            elif lexeme.value == KeyWords.EXIT:
                return self._parse_exit()
            elif lexeme.value == KeyWords.BREAK:
                return self._parse_break()
            elif lexeme.value == KeyWords.CONTINUE:
                return self._parse_continue()
            else:
                raise ParserError("Unexpected lexeme: " + str(lexeme), self._fname, lexeme.line_num, lexeme.col_num)
        elif lexeme.type == LexemTypes.DELIMITER:
            if lexeme.value == Delimiters.OPEN_BRACES:
                return self._parse_block_code()
            else:
                raise ParserError("Unexpected lexeme: " + str(lexeme), self._fname, lexeme.line_num, lexeme.col_num)
        elif lexeme.type == LexemTypes.IDENTIFIER:
            identifier_node = self._parse_using_identifier()
            node = self._parse_assignment(identifier_node)
            self._expect_delimiter(Delimiters.SEMICOLON)
            self._go_to_next_lexeme()
            return node
        else:
            raise ParserError("Unexpected lexeme: " + str(lexeme), self._fname, lexeme.line_num, lexeme.col_num)

    def parse(self):
        while self._are_lexemes_remaining():
            node = self._parse_statement()
            self._root.add_child(node)
