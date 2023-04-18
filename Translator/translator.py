from tables import LiteralTable
from lexical_analyzer import LexicalAnalyzer, LexicalAnalyzerError
from parser import Parser, ParserError
from semantic_analyzer import SemanticAnalyzer, SemanticError


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
