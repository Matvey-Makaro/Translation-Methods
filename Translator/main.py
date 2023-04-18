from lexical_analyzer import *
from parser import Parser, ParserError
from semantic_analyzer import SemanticAnalyzer, SemanticError
from translator import Translator


def main() -> None:
    # fname = input("Enter file name: ")
    fname = "test.cpp"
    try:
        translator = Translator(fname)
        translator.translate()
    except LexicalAnalyzerError as ex:
        print(ex)
    except ParserError as ex:
        print(ex)
    except SemanticError as ex:
        print(ex)


if __name__ == '__main__':
    main()
