from common import *
from tables import *
from parser import Node

class SemanticError(Exception):
    def __init__(self, text: str, fname: str, line_num: int, ch_num: int):
        self._txt = 'File "' + fname + '", line ' + str(line_num) + ' col ' + str(ch_num) + ': ' + text
        super().__init__(self._txt)


class DivisionByZeroError(SemanticError):
    def __init__(self, fname: str, line_num: int, ch_num: int):
        super().__init__("Division by zero.", fname, line_num, ch_num)


# class IntExpected(SemanticError):
#     def __init__(self, fname: str, line_num: int, ch_num: int):
#         super().__init__("Int exp")


class SemanticAnalyzer:
    def __init__(self, fname: str, root: Node, literal_table: LiteralTable, variable_table: list):
        self._fname = fname
        self._root = root
        self._literal_table = literal_table
        self._variable_table = variable_table
        self._analyze(self._root)

    def _check_int_expr(self, node: Node):
        if node is None:
            return

        lexeme = node.get_lexeme()
        if lexeme.type == LexemTypes.DOUBLE_NUM:
            raise SemanticError("Int expected.", self._fname, lexeme.line_num, lexeme.col_num)
        if lexeme.value == KeyWords.STOD:
            raise SemanticError("Int expected.", self._fname, lexeme.line_num, lexeme.col_num)
        if lexeme.value == KeyWords.STOI:
            return
        if lexeme.type == LexemTypes.IDENTIFIER and self._variable_table[lexeme.value].type == VariableTypes.DOUBLE:
            raise SemanticError("Int expected.", self._fname, lexeme.line_num, lexeme.col_num)

        for ch in node.get_childs():
            self._check_int_expr(ch)



    def _analyze(self, node: Node = None):
        if node is None:
            return
        childs = node.get_childs()
        if node.get_lexeme() is not None:
            if node.get_lexeme().value == Operators.SLASH:
                rhs = childs[1].get_lexeme()
                if rhs.type == LexemTypes.INT_NUM:
                    if int(self._literal_table.get(rhs.value).value) == 0:
                        raise DivisionByZeroError(self._fname, rhs.line_num, rhs.col_num)
                if rhs.type == LexemTypes.DOUBLE_NUM:
                    if float(self._literal_table.get(rhs.value).value) == 0.0:
                        raise DivisionByZeroError(self._fname, rhs.line_num, rhs.col_num)
            if node.get_lexeme().value == Operators.PERCENT:
                self._check_int_expr(childs[0])
                self._check_int_expr(childs[1])
                return

        for child in childs:
            self._analyze(child)
