from typing import List


class EntryPoint:
    def __init__(self, coord: List[List[float]]):
        self.open_space_coord = coord

    def __str__(self):
        return f'OSP_COORD: {self.open_space_coord}'
