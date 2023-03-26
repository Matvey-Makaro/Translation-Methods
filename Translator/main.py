from lexical_analyzer import *
from parser import Parser


def main() -> None:
    # fname = input("Enter file name: ")
    fname = "test.cpp"
    literal_table = LiteralTable()
    variable_table = []
    try:
        lex_analyzer = LexicalAnalyzer(fname, literal_table, variable_table)
        lexemes = lex_analyzer.get_lexemes()
        for lexem in lexemes:
            print(lexem)
        parser = Parser(fname, lexemes, literal_table, variable_table)
    except LexicalAnalyzerError as ex:
        print(ex)

    print('######################################################################################')
    print("Literal table: ")
    # print(literal_table._name_table)
    for i in literal_table._literals:
        print(i)

    print('######################################################################################')
    print("Variable table: ")
    for i in variable_table:
        print(i)


if __name__ == '__main__':
    main()
