from common import *
from dataclasses import dataclass


@dataclass()
class LiteralTableItem:
    type: LiteralTypes
    id: int
    value: str


class LiteralTable:
    def __init__(self):
        self._literal_to_table_item = {}
        self._literals = []

    def push(self, value: str, type: LiteralTypes) -> int:
        if value in self._literal_to_table_item:
            return self._literal_to_table_item.get(value).id

        id = len(self._literals)
        table_item = LiteralTableItem(type, id, value)
        self._literals.append(table_item)
        self._literal_to_table_item[value] = table_item
        return id

    def get(self, id: int) -> LiteralTableItem:
        return self._literals[id]

    def get_literals(self) -> list:
        return self._literals


@dataclass()
class VariableTableItem:
    name: str
    type: VariableTypes
    block_level: int
    block_id: int
    is_array: bool = False,
    dimensions: list = 0
    value = None
