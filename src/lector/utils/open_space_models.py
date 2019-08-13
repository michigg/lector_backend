from datetime import datetime
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
        self.blocked = None
        if 'blocked' in data:
            self.blocked = datetime.strptime(data['blocked'], "%Y-%m-%d")

    def is_blocked(self):
        if self.blocked:
            return datetime.now() > self.blocked
        return False

    def __str__(self):
        return f'BuildingEntryPoint:\n\tOSP_COORD: {self.open_space_coord}\n\tOSP_NODE_ID: {self.open_space_node_id}\n\tGRAPH NODE ID: {self.nearest_graph_node_id}\n\tGRAPH COORD: {self.graph_entry_node_coord}\n\tWHEELCHAIR: {self.wheelchair}'


class BBox:
    def __init__(self, max_lat: float, min_lat: float, max_lon: float, min_lon: float):
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_lon = min_lon
        self.max_lon = max_lon

    def get_bbox(self) -> List[float]:
        return [self.max_lat, self.min_lat, self.max_lon, self.min_lon]


class OpenSpace:
    def __init__(self, file_name: str, walkable_area: List[List[float]], restricted_areas: List[List[List[float]]],
                 blocked_areas: List[List[List[float]]], entry_points: List[EntryPoint], buildings=None):
        self.file_name = file_name
        self.walkable_area_coords = walkable_area
        self.restricted_areas_coords = restricted_areas
        self.blocked_areas_coords = blocked_areas
        self.entry_points = entry_points
        self.buildings = buildings

    def is_contained_building(self, building) -> bool:
        bbox = self.get_boundaries(boundary_degree_extension=0.0005)
        for staircase in building.staircases:
            # TODO check bbox
            if bbox.max_lat >= staircase.coord[1] >= bbox.min_lat and bbox.max_lon >= staircase.coord[
                0] >= bbox.min_lon:
                return True
        return False

    def set_buildings(self, buildings):
        self.buildings = [building for building in buildings if self.is_contained_building(building)]

    def get_boundaries(self, boundary_degree_extension=0.0) -> BBox:
        longitudes, latitudes = zip(*self.walkable_area_coords)

        min_lat = min(latitudes) - boundary_degree_extension
        max_lat = max(latitudes) + boundary_degree_extension
        min_lon = min(longitudes) - boundary_degree_extension
        max_lon = max(longitudes) + boundary_degree_extension
        return BBox(max_lat, min_lat, max_lon, min_lon)

# class OpenSpace:
#     def __init__(self, file_name: str, walkable_area: List, restricted_areas: List, entry_points: List[EntryPoint]):
#         self.file_name = file_name
#         self.walkable_area = walkable_area
#         self.restricted_areas = restricted_areas
#         self.entry_points = entry_points
#
#     def get_boundaries(self):
#         min_lat = 360
#         max_lat = -360
#         min_lon = 360
#         max_lon = -360
#         boundary_extetion = 0.0005
#         for coord in self.walkable_area:
#             min_lat = coord[1] if coord[1] < min_lat else min_lat
#             max_lat = coord[1] if coord[1] > max_lat else max_lat
#             min_lon = coord[0] if coord[0] < min_lon else min_lon
#             max_lon = coord[0] if coord[0] > max_lon else max_lon
#
#         min_lat -= boundary_extetion
#         max_lat += boundary_extetion
#         min_lon -= boundary_extetion
#         max_lon += boundary_extetion
#         return [max_lat, min_lat, max_lon, min_lon]
