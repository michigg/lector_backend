import logging
from typing import List

from indoor_mapper.utils.building_models import GraphStairCase, GraphBuilding, StairCase, Building
from indoor_mapper.utils.config_controller import IndoorMapperConfigController
from indoor_mapper.utils.univis_room_controller import UnivISRoomController

# from lector.utils.osmm import OSMManipulator as OSMUtils
from lector.utils.open_space_models import OpenSpace

logger = logging.getLogger(__name__)


class IndoorMapController:
    def __init__(self, osmm):
        self.univis_c = UnivISRoomController()
        self.indoor_cc = IndoorMapperConfigController()
        self.graph_buildings = None
        self.osmm = osmm

    def get_buildings_for_open_space(self, open_space: OpenSpace):
        bbox = open_space.get_boundaries()
        buildings = []
        for building in self.indoor_cc.buildings:
            for staircase in building.staircases:
                if bbox[0] > staircase.coord[0] > bbox[1] and bbox[2] > staircase[1] > bbox[3]:
                    buildings.append(building)
        return buildings

    def add_buildings_to_graph(self, buildings: List[GraphBuilding]):
        for building in buildings:
            for staircase in building.graph_staircases:
                for entry_point in staircase.entries:
                    self.osmm.set_nearest_point_to_entry(entry_point)
                self.osmm.add_entry_edges(staircase.entries)
                self.add_staircase_edges(staircase)

    def indoor_maps_to_graph(self) -> List[GraphBuilding]:
        return self.get_graph_buildings(self.indoor_cc.buildings)

    def get_graph_buildings(self, buildings: List[Building]) -> List[GraphBuilding]:
        graph_buildings = []
        for building in buildings:
            graph_stair_cases = []
            for staircase in building.staircases:
                position_id = self.osmm.add_osm_node(staircase.coord)
                for entry in staircase.entries:
                    entry.open_space_node_id = self.osmm.add_osm_node(entry.open_space_coord)
                graph_stair_cases.append(GraphStairCase(staircase, position_id))
            graph_buildings.append(GraphBuilding(building, graph_stair_cases))
        return graph_buildings

    def add_staircase_to_graph(self) -> List[GraphBuilding]:
        graph_buildings = self.indoor_maps_to_graph()
        for building in graph_buildings:
            for staircase in building.graph_staircases:
                for entry_point in staircase.entries:
                    self.osmm.set_nearest_point_to_entry(entry_point)
                self.osmm.add_entry_edges(staircase.entries)
                self.add_staircase_edges(staircase)
        return graph_buildings

    def add_staircase_edges(self, staircase: GraphStairCase):
        edges = len(self.osmm.graph.edges)
        for entry in staircase.entries:
            self.osmm.add_osm_edge(staircase.position_id, entry.open_space_node_id)
        print(f'ADDED EDGES STAIRCASE: {len(self.osmm.graph.edges) - edges}')


class RoomStaircaseController:
    def __init__(self):
        self.indoor_cc = IndoorMapperConfigController()

    def get_rooms_staircase(self, room) -> StairCase or None:
        for building in self.indoor_cc.buildings:
            if str(building.key).lower() == str(room.building_key).lower():
                logger.warn(building)
                staircase = building.get_rooms_staircase(room)
                if staircase:
                    return staircase
        return None

    def print_buildings(self):
        for building in self.indoor_cc.buildings:
            print(building)
