import logging
from typing import List

from indoor_mapper.utils.building_models import GraphStairCase, GraphBuilding
from indoor_mapper.utils.config_controller import IndoorMapperConfigController
from indoor_mapper.utils.univis_room_controller import UnivISRoomController
from lector.utils.open_space_models import EntryPoint

# from lector.utils.osmm import OSMManipulator as OSMUtils

logger = logging.getLogger(__name__)


class IndoorMapController:
    def __init__(self, osmm):
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
                    self.osmm.set_nearest_point_to_entry(entry_point)
                self.osmm.add_entry_edges(staircase.entry_points)
                self.add_staircase_edges(staircase)

    def add_staircase_edges(self, staircase: GraphStairCase):
        edges = len(self.graph.edges)
        for entry in staircase.entry_points:
            self.osmm.add_osm_edge(staircase.position_id, entry.open_space_node_id)
        print(f'ADDED EDGES STAIRCASE: {len(self.graph.edges) - edges}')

    def print_buildings(self):
        for building in self.indoor_cc.buildings:
            print(building)
