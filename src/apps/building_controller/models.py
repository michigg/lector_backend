import re
from datetime import datetime
from typing import List

from apps.lector.models import EntryPoint


class Room:
    def __init__(self, building_key=None, level=None, number=None):
        self.building_key = building_key
        self.number = number
        self.level = int(level)

    def get_number(self):
        pattern = re.compile('([0-9]*).*')
        match = pattern.match(self.number)
        return int(match.group())

    def __str__(self):
        return f'{self.building_key}/{self.level:02d}.{self.number}'


class Floor:
    def __init__(self, level: int or str, ranges: List[List[int]]):
        self.level = level
        self.ranges = ranges

    def is_floor_room(self, room: Room):
        for range in self.ranges:
            if range[0] <= room.get_number() <= range[1]:
                return True
        return False


class BuildingEntryPoint(EntryPoint):
    def __init__(self, data: dict):
        super().__init__(data['coord'])
        self.wheelchair = data['wheelchair']
        self.blocked = None
        if 'blocked' in data:
            self.blocked = datetime.strptime(data['blocked'], "%Y-%m-%d")

    def is_blocked(self):
        if self.blocked:
            return datetime.now() < self.blocked
        return False

    def __str__(self):
        return f'BuildingEntryPoint:\n\tOSP_COORD: {self.open_space_coord}\n\tOSP_NODE_ID: {self.open_space_node_id}\n\tGRAPH NODE ID: {self.nearest_graph_node_id}\n\tGRAPH COORD: {self.graph_entry_node_coord}\n\tWHEELCHAIR: {self.wheelchair}'


class StairCase:
    def __init__(self, name, floors: List[Floor], coord, entries: List[BuildingEntryPoint], blocked=None,
                 neighbours=None, wheelchair=False):
        self.name = name
        self.coord = coord
        self.entries = entries
        self.floors = floors
        self.rooms = []
        self.blocked = blocked
        self.neighbours = neighbours
        self.wheelchair = wheelchair

    def add_room(self, room: Room):
        self.rooms.append(room)
        self.rooms.sort(key=lambda x: x.number)

    def is_staircase_room(self, room: Room):
        for floor in self.floors:
            if room.level == floor.level and floor.is_floor_room(room):
                return True
        return False

    def get_not_blocked_entries(self):
        if self.is_blocked():
            return []
        return [entry for entry in self.entries if not entry.is_blocked()]

    def is_blocked(self):
        if self.blocked:
            return datetime.now() < self.blocked
        return False

    def __str__(self):
        output = f'Staircase {self.name}\n'
        for room in self.rooms:
            output += f'{room}, '
        return output


class Building:
    def __init__(self, key, staircases: List[StairCase]):
        self.key = key
        self.staircases = staircases

    def get_rooms_staircase(self, room: Room):
        for staircase in self.staircases:
            if staircase.is_staircase_room(room):
                return staircase
        return None

    def __str__(self):
        output = f'Building {self.key}\n'
        for staircase in self.staircases:
            output += f'{staircase}\n'
        return output
