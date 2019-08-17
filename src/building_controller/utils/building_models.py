from datetime import datetime
from typing import List

from lector.utils.open_space_models import BuildingEntryPoint, GraphBuildingEntryPoint


class Room:
    def __init__(self, building_key=None, level=None, number=None):
        self.building_key = building_key
        self.number = int(number)
        self.level = int(level)

    def __str__(self):
        return f'{self.building_key}/{self.level:02d}.{self.number:03d}'


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
    def __init__(self, name, floors: List[Floor], coord, entries: List[BuildingEntryPoint], blocked=None,
                 neighbours=None):
        self.name = name
        self.coord = coord
        self.entries = entries
        self.floors = floors
        self.rooms = []
        self.blocked = blocked
        self.neighbours = neighbours

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


class GraphStairCase(StairCase):
    def __init__(self, staircase: StairCase, position_id: int, graph_entries: List[GraphBuildingEntryPoint]):
        super().__init__(staircase.name, staircase.floors, staircase.coord, staircase.entries, staircase.blocked,
                         staircase.neighbours)
        self.position_id = position_id
        self.graph_entries = graph_entries

    def get_not_blocked_entries(self):
        if self.is_blocked():
            return []
        return [entry for entry in self.graph_entries if not entry.is_blocked()]


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


class GraphBuilding(Building):
    def __init__(self, osmm, building: Building, graph_staircases: List[GraphStairCase]):
        super().__init__(building.key, building.staircases)
        self.osmm = osmm
        self.graph_staircases = graph_staircases

    def get_staircaise_neighbours(self, staircase: StairCase):
        if staircase.neighbours:
            return [graph_staircase for graph_staircase in self.graph_staircases if
                    graph_staircase.name in staircase.neighbours]
        return []

    def add_staircase_edges(self):
        for graph_staircase in self.graph_staircases:
            if not graph_staircase.is_blocked():
                for entry in graph_staircase.graph_entries:
                    if not entry.is_blocked():
                        self.osmm.add_osm_edge(graph_staircase.position_id, entry.nearest_graph_node_id, self.key)
                        entry.add_edges()
            for alternate_staircase in self.get_staircaise_neighbours(graph_staircase):
                self.osmm.add_osm_edge(graph_staircase.position_id,
                                       alternate_staircase.position_id,
                                       maxspeed=0.01,
                                       name=self.key)