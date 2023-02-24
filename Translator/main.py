from lexical_analyzer import *


def main() -> None:
    # fname = input("Enter file name: ")
    fname = "test.cpp"
    name_table = NameTable()
    try:
        lex_analyzer = LexicalAnalyzer(fname, name_table)
        lexemes = lex_analyzer.get_lexemes()
        for lexem in lexemes:
            print(lexem)
    except LexicalAnalyzerError as ex:
        print(ex)

    print('######################################################################################')
    # print(name_table._name_table)
    for i in name_table._name_table.items():
        print(i)


if __name__ == '__main__':
    main()
