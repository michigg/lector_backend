from typing import List

import logging

logger = logging.getLogger(__name__)


class EntryPoint:
    def __init__(self, coord: List[List[float]]):
        self.open_space_coord = coord
        self.open_space_node_id = None
        self.nearest_graph_node_id = None
        self.graph_entry_node_coord = None
        self.graph_entry_edge = []

    def __str__(self):
        return f'OSP_COORD: {self.open_space_coord}\nOSP_NODE_ID: {self.open_space_node_id}\nGRAPH NODE ID: {self.nearest_graph_node_id}\nGRAPH COORD: {self.graph_entry_node_coord}'


class OpenSpaceEntryPoint(EntryPoint):
    def __init__(self, coord: List[List[float]]):
        super().__init__(coord)


class BuildingEntryPoint(EntryPoint):
    def __init__(self, data: dict):
        super().__init__(data['coord'])
        self.wheelchair = data['wheelchair']

    def __str__(self):
        return f'BuildingEntryPoint:\n\tOSP_COORD: {self.open_space_coord}\n\tOSP_NODE_ID: {self.open_space_node_id}\n\tGRAPH NODE ID: {self.nearest_graph_node_id}\n\tGRAPH COORD: {self.graph_entry_node_coord}\n\tWHEELCHAIR: {self.wheelchair}'


class OpenSpace:
    def __init__(self, walkable_area: List, restricted_areas: List, entry_points: List[EntryPoint]):
        self.walkable_area = walkable_area
        self.restricted_areas = restricted_areas
        self.entry_points = entry_points
