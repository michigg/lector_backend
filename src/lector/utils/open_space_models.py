from datetime import datetime
from typing import List

import logging

from shapely.geometry import Point
from shapely.ops import nearest_points

logger = logging.getLogger(__name__)


class EntryPoint:
    def __init__(self, coord: List[List[float]]):
        self.open_space_coord = coord

    def __str__(self):
        return f'OSP_COORD: {self.open_space_coord}'


class GraphEntryPoint(EntryPoint):
    def __init__(self, entry_point: EntryPoint, osmm):
        super().__init__(coord=entry_point.open_space_coord)
        self.osmm = osmm
        self.open_space_node_id = self.osmm.add_osm_node(self.open_space_coord)
        self.open_space_point = Point(*self.open_space_coord)
        self.graph_entry_node_coord = None
        self.graph_entry_edge = None

        self._set_nearest_graph_entry_node_and_edge()
        self.nearest_graph_node_id = self.osmm.add_osm_node(self.graph_entry_node_coord)

    def _set_nearest_graph_entry_node_and_edge(self):
        nearest_edge = self.osmm.get_nearest_edge(self.open_space_coord)
        nearest_point = nearest_points(self.open_space_point, nearest_edge[0])[1]
        self.graph_entry_node_coord = [nearest_point.x, nearest_point.y]
        self.graph_entry_edge = [nearest_edge[1], nearest_edge[2]]

    def add_edges(self):
        self.osmm.add_osm_edge(self.graph_entry_edge[0], self.nearest_graph_node_id, "Test")
        self.osmm.add_osm_edge(self.graph_entry_edge[1], self.nearest_graph_node_id, "Test")
        self.osmm.add_osm_edge(self.open_space_node_id, self.nearest_graph_node_id, "Test")


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


class GraphBuildingEntryPoint(BuildingEntryPoint, GraphEntryPoint):
    def __init__(self, entry_point: BuildingEntryPoint, osmm):
        self.wheelchair = entry_point.wheelchair
        self.blocked = entry_point.blocked
        GraphEntryPoint.__init__(self, entry_point=entry_point, osmm=osmm)


class GraphOpenSpaceEntryPoint(OpenSpaceEntryPoint, GraphEntryPoint):
    def __init__(self, entry_point: OpenSpaceEntryPoint, osmm):
        self.open_space_coord = entry_point.open_space_coord
        print(self.open_space_coord)
        GraphEntryPoint.__init__(self, entry_point=entry_point, osmm=osmm)
