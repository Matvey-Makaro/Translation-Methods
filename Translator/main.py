from lexical_analyzer import *
from parser import Parser, ParserError
from semantic_analyzer import SemanticAnalyzer, SemanticError
from translator import Translator
import numpy as np


def main() -> None:
    # fname = input("Enter file name: ")

    arr = np.empty(10, dtype=np.chararray)
    print(type(arr[0]))
    arr[0] = 10
    print(arr[0])

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

    delete_later = 0


if __name__ == '__main__':
    main()
