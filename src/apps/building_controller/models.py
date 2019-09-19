import re
from datetime import datetime
from typing import List

from apps.lector.models import EntryPoint

import logging

logger = logging.getLogger(__name__)


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

    def __eq__(self, other):
        return self.building_key == other.building_key \
               and self.number == other.blocked \
               and self.level == other.level


class Floor:
    def __init__(self, level: int or str, ranges: List[List[int]]):
        self.level = level
        self.ranges = ranges

    def is_floor_room(self, room: Room):
        for range in self.ranges:
            if range[0] <= room.get_number() <= range[1]:
                return True
        return False

    def __eq__(self, other):
        return self.level == other.level \
               and self.ranges == other.ranges


class BuildingEntryPoint(EntryPoint):
    def __init__(self, data: dict):
        super().__init__(data['coord'])
        self.wheelchair = data.get('wheelchair', False)
        self.blocked = None
        if 'blocked' in data:
            self.blocked = datetime.strptime(data['blocked'], "%Y-%m-%d")

    def is_blocked(self):
        if self.blocked:
            return datetime.now() < self.blocked
        return False

    def __str__(self):
        return f'BuildingEntryPoint:\n\tOSP_COORD: {self.open_space_coord}\n\tWHEELCHAIR: {self.wheelchair}'

    def __eq__(self, other):
        return self.wheelchair == other.wheelchair \
               and self.blocked == other.blocked \
               and self.open_space_coord == other.open_space_coord


class StairCase:
    def __init__(self, id: int, name: str, floors: List[Floor], coord, entries: List[BuildingEntryPoint], blocked=None,
                 neighbours=None, wheelchair=False):
        self.id = id
        self.name = name
        self.coord = coord
        self.entries = entries
        self.floors = floors
        self.blocked = blocked
        self.neighbours = neighbours
        self.wheelchair = wheelchair

    def is_staircase_room(self, room: Room):
        for floor in self.floors:
            if room.level == floor.level and floor.is_floor_room(room):
                return True
        return False

    def get_not_blocked_entries(self) -> List[BuildingEntryPoint]:
        return [entry for entry in self.entries if not entry.is_blocked()] if self.is_blocked() else []

    def is_blocked(self):
        return datetime.now() < self.blocked if self.blocked else False

    def __str__(self):
        return f'Staircase ID:{self.id}\n\tName: {self.name}\n\tBlocked: {self.blocked}\n\tNeighbours: {self.neighbours}'

    def __eq__(self, other):
        return self.id == other.id \
               and self.name == other.name \
               and self.coord == other.coord \
               and self.entries == other.entries \
               and self.floors == other.floors \
               and self.blocked == other.blocked \
               and self.neighbours == other.neighbours \
               and self.wheelchair == other.wheelchair


class Building:
    def __init__(self, key, staircases: List[StairCase]):
        self.key = key
        self.staircases = staircases

    def get_rooms_staircase(self, room: Room) -> StairCase or None:
        for staircase in self.staircases:
            if staircase.is_staircase_room(room):
                return staircase
        return None

    def __str__(self):
        output = f'Building {self.key}\n'
        for staircase in self.staircases:
            output += f'{staircase}\n'
        return output

    def __eq__(self, other):
        return self.key == other.key \
               and self.staircases == other.staircases
