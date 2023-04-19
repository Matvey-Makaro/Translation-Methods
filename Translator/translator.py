from lexical_analyzer import LexicalAnalyzer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from common import *
from tables import *


class Translator:
    def __init__(self, fname: str):
        self._fname = fname
        self._literal_table = LiteralTable()
        self._variable_table = []
        self._lex_analyzer = None
        self._lexemes = None
        self._parser = None
        self._root = None
        self._semantic_analyzer = None

    def print_lexemes(self) -> None:
        for lexeme in self._lexemes:
            print(lexeme)

    def get_lexemes(self) -> list:
        return self._lexemes

    def print_literal_table(self) -> None:
        for literal in self._literal_table.get_literals():
            print(literal)

    def get_literal_table(self) -> LiteralTable:
        return self._literal_table

    def print_variable_table(self) -> None:
        for var in self._variable_table:
            print(var)

    def get_variable_table(self) -> list:
        return self._variable_table

    def print_syntax_tree(self) -> None:
        self._parser.print_syntax_tree()

    def translate(self) -> None:
        self._lex_analyzer = LexicalAnalyzer(self._fname, self._literal_table, self._variable_table)
        self._lexemes = self._lex_analyzer.get_lexemes()
        self.print_lexemes()
        self._parser = Parser(self._fname, self._lexemes, self._literal_table, self._variable_table)

        print('######################################################################################')
        print("Literal table: ")
        self.print_literal_table()

        print('######################################################################################')
        print("Variable table: ")
        self.print_variable_table()

        print('######################################################################################')
        print("Syntax tree: ")
        self.print_syntax_tree()

        self._root = self._parser.get_tree()
        self._semantic_analyzer = SemanticAnalyzer(self._fname, self._root, self._literal_table, self._variable_table)

        print('######################################################################################')
        print("Program execution:")
        self._execute_code(self._root)

    def _get_variable(self, lexeme: LexTableItem) -> VariableTableItem:
        return self._variable_table[lexeme.value]

    def _execute_code_block(self, code_block_node: Node):
        for child in code_block_node.get_childs():
            self._execute_code(child)

    def _declare_var(self, declaration_node: Node):
        childs = declaration_node.get_childs()
        assert (len(childs) == 2)
        self._execute_code(childs[1])

    def _execute_true(self, node: Node) -> bool:
        assert (node.get_lexeme().value == KeyWords.TRUE)
        return True

    def _execute_false(self, node: Node) -> bool:
        assert (node.get_lexeme().value == KeyWords.FALSE)
        return False

    def _execute_while(self, node: Node) -> None:
        assert (node.get_lexeme().value == KeyWords.WHILE)
        childs = node.get_childs()
        assert (len(childs) == 2)
        condition_node = childs[0]
        body_node = childs[1]

        while self._execute_code(condition_node):
            self._execute_code(body_node)

    def _execute_print(self, node: Node) -> None:
        assert (node.get_lexeme().value == KeyWords.PRINT)
        childs = node.get_childs()
        assert (len(childs) == 1)
        string = self._execute_code(childs[0])
        print(string, end='')

    def _execute_scan(self, node: Node) -> str:
        assert (node.get_lexeme().value == KeyWords.SCAN)
        childs = node.get_childs()
        assert (len(childs) == 0)
        return input()

    def _execute_to_string(self, node: Node) -> str:
        assert (node.get_lexeme().value == KeyWords.TO_STRING)
        childs = node.get_childs()
        assert (len(childs) == 1)
        child = childs[0]
        arg = self._execute_code(child)
        try:
            string = str(arg)
        except Exception:
            lexeme = child.get_lexeme()
            print("Runtime error! File: ", self._fname, "line: ", lexeme.line_num, " col: ", lexeme.col_num,
                  ": Error on type conversion to string.")
            exit(-1)
        return string

    def _execute_stoi(self, node: Node) -> int:
        assert (node.get_lexeme().value == KeyWords.STOI)
        childs = node.get_childs()
        assert (len(childs) == 1)
        child = childs[0]
        arg = self._execute_code(child)
        try:
            number = int(arg)
        except Exception:
            lexeme = child.get_lexeme()
            print("Runtime error! File:", self._fname, "line:", lexeme.line_num, "col:", lexeme.col_num,
                  ": Error on type conversion to int.")
            exit(-1)
        return number

    def _execute_stod(self, node: Node) -> float:
        assert (node.get_lexeme().value == KeyWords.STOD)
        childs = node.get_childs()
        assert (len(childs) == 1)
        child = childs[0]
        arg = self._execute_code(child)
        try:
            number = float(arg)
        except Exception:
            lexeme = child.get_lexeme()
            print("Runtime error! File:", self._fname, "line:", lexeme.line_num, "col:", lexeme.col_num,
                  ": Error on type conversion to double.")
            exit(-1)
        return number

    def _execute_exit(self, node: Node) -> None:
        assert (node.get_lexeme().value == KeyWords.EXIT)
        childs = node.get_childs()
        assert (len(childs) == 1)
        arg = self._execute_code(childs[0])
        exit(arg)

    def _execute_key_words(self, node: Node):
        key_word = node.get_lexeme().value
        if key_word == KeyWords.TRUE:
            return self._execute_true(node)
        elif key_word == KeyWords.FALSE:
            return self._execute_false(node)
        elif key_word == KeyWords.NULLPTR:  # TODO: Do.
            pass
        elif key_word == KeyWords.WHILE:
            return self._execute_while(node)
        elif key_word == KeyWords.CONTINUE:
            pass
        elif key_word == KeyWords.BREAK:
            pass
        elif key_word == KeyWords.IF:
            pass
        elif key_word == KeyWords.ELSE:
            pass
        elif key_word == KeyWords.PRINT:
            return self._execute_print(node)
        elif key_word == KeyWords.SCAN:
            return self._execute_scan(node)
        elif key_word == KeyWords.TO_STRING:
            return self._execute_to_string(node)
        elif key_word == KeyWords.STOI:
            return self._execute_stoi(node)
        elif key_word == KeyWords.STOD:
            return self._execute_stod(node)
        elif key_word == KeyWords.EXIT:
            return self._execute_exit(node)
        elif key_word in (
                KeyWords.INT, KeyWords.DOUBLE, KeyWords.BOOL, KeyWords.STRING, KeyWords.VOID):  # TODO: do void
            return None

    def _execute_equal(self, node: Node):
        assert (node.get_lexeme().value == Operators.EQUAL)
        childs = node.get_childs()
        assert (len(childs) == 2)
        lhs_lexeme = childs[0].get_lexeme()
        lhs_var = self._get_variable(lhs_lexeme)
        lhs_var.value = self._execute_code(childs[1])
        return None

    def _execute_unary_operation(self, node: Node, func):
        childs = node.get_childs()
        assert (len(childs) == 1)
        value = self._execute_code(childs[0])
        return func(value)

    def _execute_binary_operation(self, node: Node, func):
        childs = node.get_childs()
        assert (len(childs) == 2)
        lhs = self._execute_code(childs[0])
        rhs = self._execute_code(childs[1])
        return func(lhs, rhs)

    def _execute_plus_operation(self, node: Node):
        num_of_childs = len(node.get_childs())
        if num_of_childs == 1:
            return self._execute_unary_operation(node, lambda x: +x)
        elif num_of_childs == 2:
            return self._execute_binary_operation(node, lambda lhs, rhs: lhs + rhs)
        else:
            assert 0

    def _execute_minus_operation(self, node: Node):
        num_of_childs = len(node.get_childs())
        if num_of_childs == 1:
            return self._execute_unary_operation(node, lambda x: -x)
        elif num_of_childs == 2:
            return self._execute_binary_operation(node, lambda lhs, rhs: lhs - rhs)
        else:
            assert 0

    def _execute_operators(self, node: Node):
        lexeme = node.get_lexeme()
        if lexeme.value == Operators.EQUAL:
            return self._execute_equal(node)
        elif lexeme.value == Operators.NOT:
            # return self._execute_not(node)
            return self._execute_unary_operation(node, lambda x: not x)
        elif lexeme.value == Operators.DOUBLE_EQUAL:
            return self._execute_binary_operation(node, lambda lhs, rhs: lhs == rhs)
        elif lexeme.value == Operators.NOT_EQUAL:
            return self._execute_binary_operation(node, lambda lhs, rhs: lhs != rhs)
        elif lexeme.value == Operators.LESS:
            return self._execute_binary_operation(node, lambda lhs, rhs: lhs < rhs)
        elif lexeme.value == Operators.LESS_OR_EQUAL:
            return self._execute_binary_operation(node, lambda lhs, rhs: lhs <= rhs)
        elif lexeme.value == Operators.GREATER:
            return self._execute_binary_operation(node, lambda lhs, rhs: lhs > rhs)
        elif lexeme.value == Operators.GREATER_OR_EQUAL:
            return self._execute_binary_operation(node, lambda lhs, rhs: lhs >= rhs)
        elif lexeme.value == Operators.AND:
            return self._execute_binary_operation(node, lambda lhs, rhs: lhs and rhs)
        elif lexeme.value == Operators.OR:
            return self._execute_binary_operation(node, lambda lhs, rhs: lhs or rhs)
        elif lexeme.value == Operators.PLUS:
            return self._execute_plus_operation(node)
        elif lexeme.value == Operators.MINUS:
            return self._execute_minus_operation(node)
        elif lexeme.value == Operators.ASTERISK:
            return self._execute_binary_operation(node, lambda lhs, rhs: lhs * rhs)
        elif lexeme.value == Operators.SLASH:
            return self._execute_binary_operation(node, lambda lhs, rhs: lhs / rhs)
        elif lexeme.value == Operators.PERCENT:
            return self._execute_binary_operation(node, lambda lhs, rhs: lhs % rhs)
        elif lexeme.value == Operators.AMPERSAND:
            pass  # TODO: DO
        else:
            raise RuntimeError("Unreachable!")

    def _execute_identifier(self, node: Node):
        lexeme = node.get_lexeme()
        assert (lexeme.type == LexemTypes.IDENTIFIER)
        var = self._get_variable(lexeme)
        return var.value

    def _execute_literal(self, node: Node):
        lexeme = node.get_lexeme()
        assert (is_literal(lexeme))
        literal = self.get_literal_table().get(lexeme.value)

        if lexeme.type == LexemTypes.INT_NUM:
            return int(literal.value)
        elif lexeme.type == LexemTypes.DOUBLE_NUM:
            return float(literal.value)
        elif lexeme.type == LexemTypes.STRING:
            return literal.value
        else:
            assert 0

    def _execute_common(self, node: Node):
        lexeme = node.get_lexeme()
        if lexeme.type == LexemTypes.KEY_WORD:
            return self._execute_key_words(node)
        elif lexeme.type == LexemTypes.OPERATOR:
            return self._execute_operators(node)
        elif lexeme.type == LexemTypes.IDENTIFIER:
            return self._execute_identifier(node)
        elif is_literal(lexeme):
            return self._execute_literal(node)
        else:
            raise RuntimeError("Unreachable")

    def _execute_code(self, node: Node):
        if node is None:
            return
        node_type = node.get_type()
        if node_type == NodeTypes.COMMON:
            return self._execute_common(node)
        elif node_type == NodeTypes.CODE_BLOCK:
            return self._execute_code_block(node)
        elif node_type == NodeTypes.DECLARATION:
            return self._declare_var(node)
        elif node_type == NodeTypes.INDEX_APPEAL:
            pass
        else:
            raise RuntimeError("Unreachable!")
