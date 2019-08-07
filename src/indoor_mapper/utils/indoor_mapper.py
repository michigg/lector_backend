import logging
from typing import List

from indoor_mapper.utils.building_models import GraphStairCase, GraphBuilding, StairCase
from indoor_mapper.utils.config_controller import IndoorMapperConfigController
from indoor_mapper.utils.univis_room_controller import UnivISRoomController

# from lector.utils.osmm import OSMManipulator as OSMUtils

logger = logging.getLogger(__name__)


class IndoorMapController:
    def __init__(self, osmm):
        self.univis_c = UnivISRoomController()
        self.indoor_cc = IndoorMapperConfigController()
        self.graph_buildings = None
        self.osmm = osmm
        self.graph = osmm.graph

    # def load_indoor_map_data(self):
    #     for building in self.indoor_cc.buildings:
    #         rooms = self.univis_c.get_rooms_by_building_key(building.key)
    #         for room in rooms:
    #             for staircase in building.staircases:
    #                 if staircase.is_staircase_room():
    #                     staircase.add_room(room)
    #                     rooms.pop()

    def indoor_maps_to_graph(self) -> List[GraphBuilding]:
        # nodes = len(self.graph.nodes)
        graph_buildings = []
        for building in self.indoor_cc.buildings:
            graph_stair_cases = []
            for staircase in building.staircases:
                position_id = self.osmm.add_osm_node(staircase.coord)
                for entry in staircase.entries:
                    entry.open_space_node_id = self.osmm.add_osm_node(entry.open_space_coord)
                graph_stair_cases.append(GraphStairCase(staircase, position_id))
            graph_buildings.append(GraphBuilding(building, graph_stair_cases))
        # print(f'ADDED NODES: {len(self.graph.nodes) - nodes}')
        return graph_buildings

    def add_staircase_to_graph(self):
        for building in self.indoor_maps_to_graph():
            for staircase in building.graph_staircases:
                for entry_point in staircase.entries:
                    self.osmm.set_nearest_point_to_entry(entry_point)
                self.osmm.add_entry_edges(staircase.entries)
                self.add_staircase_edges(staircase)

    def add_staircase_edges(self, staircase: GraphStairCase):
        edges = len(self.graph.edges)
        for entry in staircase.entries:
            self.osmm.add_osm_edge(staircase.position_id, entry.open_space_node_id)
        print(f'ADDED EDGES STAIRCASE: {len(self.graph.edges) - edges}')


class RoomStaircaseController:
    def __init__(self):
        self.indoor_cc = IndoorMapperConfigController()

    def get_rooms_staircase(self, room) -> StairCase or None:
        for building in self.indoor_cc.buildings:
            if building.key == room.building_key:
                logger.warn('STAIRCASE')
                for staircase in building.staircases:
                    if staircase.is_staircase_room(room):
                        return staircase
        return None

    def print_buildings(self):
        for building in self.indoor_cc.buildings:
            print(building)
