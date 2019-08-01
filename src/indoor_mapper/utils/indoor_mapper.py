import logging
from typing import List

import osmnx as ox
from indoor_mapper.utils.building_models import GraphStairCase, GraphBuilding
from indoor_mapper.utils.config_controller import IndoorMapperConfigController
from indoor_mapper.utils.univis_room_controller import UnivISRoomController
from lector.utils.open_space_controller import EntryPoint
from lector.utils.osmm import OSMManipulator
from shapely.geometry import Point
from shapely.ops import nearest_points

logger = logging.getLogger(__name__)


class IndoorMapController():
    def __init__(self, osmm: OSMManipulator):
        super().__init__(osmm.current_node_id, osmm.graph)
        self.univis_c = UnivISRoomController()
        self.indoor_cc = IndoorMapperConfigController()
        self.graph_buildings = None
        self.osmm = osmm
        self.graph = osmm.graph

    def load_indoor_map_data(self):
        for building in self.indoor_cc.buildings:
            rooms = self.univis_c.get_rooms_by_building_key(building.key)
            for staircase in building.staircases:
                for floor in staircase.floors:
                    for room in rooms:
                        if room.level == floor.level and floor.room_range_min <= room.number <= floor.room_range_max:
                            staircase.add_room(room)
                            rooms.pop()

    def indoor_maps_to_graph(self) -> List[GraphBuilding]:
        nodes = len(self.graph.nodes)
        graph_buildings = []
        for building in self.indoor_cc.buildings:
            graph_stair_cases = []
            for staircase in building.staircases:
                self.osmm.add_osm_node(staircase.coord)
                position_id = self.osmm.current_osm_id
                entry_points = []
                for entry in staircase.entries:
                    self.osmm.add_osm_node(entry)

                    entry_point = EntryPoint(entry)
                    entry_point.open_space_node_id = self.osmm.current_osm_id
                    entry_points.append(entry_point)
                graph_stair_cases.append(GraphStairCase(staircase, position_id, entry_points))
            graph_buildings.append(GraphBuilding(building, graph_stair_cases))
        print(f'ADDED NODES: {len(self.graph.nodes) - nodes}')
        return graph_buildings

    def add_staircase_to_graph(self):
        for building in self.indoor_maps_to_graph():
            for staircase in building.graph_staircases:
                for entry_point in staircase.entry_points:
                    self._set_nearest_point_to_entry(entry_point)
                self.add_entry_edges(staircase.entry_points)
                self.add_staircase_edges(staircase)

    def _set_nearest_point_to_entry(self, entry_point: EntryPoint) -> (Point, int, int):
        nearest_edge = ox.get_nearest_edge(self.graph, entry_point.open_space_coord[::-1])
        entry_point_shply = Point(*entry_point.open_space_coord)
        nearest_point = nearest_points(entry_point_shply, nearest_edge[0])[1]
        entry_point.graph_entry_node_coord = [nearest_point.x, nearest_point.y]
        entry_point.graph_entry_edge = [nearest_edge[1], nearest_edge[2]]

    def add_entry_edges(self, entry_points):
        edges = len(self.graph.edges)
        for entry_point in entry_points:
            self.osmm.add_osm_node(entry_point.graph_entry_node_coord)
            entry_point.nearest_graph_node_id = self.osmm.current_osm_id
            self.osmm.add_osm_edge(entry_point.graph_entry_edge[0], entry_point.nearest_graph_node_id)
            self.osmm.add_osm_edge(entry_point.graph_entry_edge[1], entry_point.nearest_graph_node_id)
            self.osmm.add_osm_edge(entry_point.nearest_graph_node_id, entry_point.open_space_node_id)
        print(f'ADDED EDGES ENTRY: {len(self.graph.edges) - edges}')

    def add_staircase_edges(self, staircase: GraphStairCase):
        edges = len(self.graph.edges)
        for entry in staircase.entry_points:
            self.osmm.add_osm_edge(staircase.position_id, entry.open_space_node_id)
        print(f'ADDED EDGES STAIRCASE: {len(self.graph.edges) - edges}')

    def print_buildings(self):
        for building in self.indoor_cc.buildings:
            print(building)
