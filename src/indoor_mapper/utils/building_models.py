from typing import List

from indoor_mapper.utils.univis_models import Room
from lector.utils.open_space_models import EntryPoint, BuildingEntryPoint


class Floor:
    def __init__(self, level: int or str, ranges: List[List[int]]):
        self.level = level
        self.ranges = ranges

    def is_floor_room(self, room: Room):
        for range in self.ranges:
            if range[0] <= room.number <= range[1]:
                return True
        return False


class StairCase:
    def __init__(self, name, floors: List[Floor], coord, entries: List[BuildingEntryPoint]):
        self.name = name
        self.coord = coord
        self.entries = entries
        self.floors = floors
        self.rooms = []

    def add_room(self, room: Room):
        # TODO: better insert sort
        self.rooms.append(room)
        self.rooms.sort(key=lambda x: x.number)

    def is_staircase_room(self, room: Room):
        for floor in self.floors:
            if room.level == floor.level and floor.is_floor_room(room):
                return True
        return False

    def __str__(self):
        output = f'Staircase {self.name}\n'
        for room in self.rooms:
            output += f'{room}, '
        return output


class GraphStairCase(StairCase):
    def __init__(self, staircase: StairCase, position_id: int):
        super().__init__(staircase.name, staircase.floors, staircase.coord, staircase.entries)
        self.position_id = position_id


class Building:
    def __init__(self, key, staircases: List[StairCase]):
        self.key = key
        self.staircases = staircases

    def get_rooms_staircase(self, room: Room):
        for staircase in self.staircases:
            if room in staircase.rooms:
                return staircase
        return None

    def __str__(self):
        output = f'Building {self.key}\n'
        for staircase in self.staircases:
            output += f'{staircase}\n'
        return output


class GraphBuilding(Building):
    def __init__(self, building: Building, graph_staircases: List[GraphStairCase]):
        super().__init__(building.key, building.staircases)
        self.graph_staircases = graph_staircases
