from typing import List

import logging

logger = logging.getLogger(__name__)


class EntryPoint:
    def __init__(self, entry_point):
        self.open_space_coord = entry_point
        self.open_space_node_id = None
        self.nearest_graph_node_id = None
        self.graph_entry_node_coord = None
        self.graph_entry_edge = []


class OpenSpace:
    def __init__(self, walkable_area: List, restricted_areas: List, entry_points: List[EntryPoint]):
        self.walkable_area = walkable_area
        self.restricted_areas = restricted_areas
        self.entry_points = entry_points
