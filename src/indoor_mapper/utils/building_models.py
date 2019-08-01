from typing import List

from indoor_mapper.utils.univis_models import Room
from lector.utils.open_space_controller import EntryPoint


class Floor:
    def __init__(self, level, room_range_min, room_range_max):
        self.level = level
        self.room_range_min = room_range_min
        self.room_range_max = room_range_max


class StairCase:
    def __init__(self, name, floors: List[Floor], coord, entries: List[List[float]]):
        self.name = name
        self.coord = coord
        self.entries = entries
        self.floors = floors
        self.rooms = []

    def add_room(self, room: Room):
        # TODO: better insert sort
        self.rooms.append(room)
        self.rooms.sort(key=lambda x: x.number)

    def __str__(self):
        output = f'Staircase {self.name}\n'
        for room in self.rooms:
            output += f'{room}, '
        return output


class GraphStairCase(StairCase):
    def __init__(self, staircase: StairCase, position_id: int, entry_ids: List[EntryPoint]):
        super().__init__(staircase.name, staircase.floors, staircase.coord, staircase.entries)
        self.position_id = position_id
        self.entry_points = entry_ids


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
