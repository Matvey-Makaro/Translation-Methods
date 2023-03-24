from lexical_analyzer import *


def is_key_word_type(key_word: KeyWords) -> bool:
    return key_word == KeyWords.INT or key_words == KeyWords.DOUBLE or \
        key_word == KeyWords.BOOL or key_word == KeyWords.STRING


class Node:
    def __init__(self, lexem):
        self._lexem = lexem
        self._childs = []

    def add_child(self, node) -> None:
        self._childs.append(node)


class Parser:
    def __init__(self, lexemes: list):
        self._lexemes = lexemes
        self.parse()

    def _parse_type(self):
        pass

    def parse(self):
        for lexem in self._lexemes:
            if lexem.type == LexemTypes.KEY_WORD:
                if is_key_word_type(lexem.value):
                    pass
