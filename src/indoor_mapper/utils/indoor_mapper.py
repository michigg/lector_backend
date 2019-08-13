import logging
from typing import List

from indoor_mapper.utils.building_models import GraphStairCase, GraphBuilding, StairCase, Building
from indoor_mapper.utils.config_controller import IndoorMapperConfigController
from indoor_mapper.utils.univis_room_controller import UnivISRoomController

# from lector.utils.osmm import OSMManipulator as OSMUtils
from lector.utils.open_space_models import OpenSpace, GraphBuildingEntryPoint

logger = logging.getLogger(__name__)


class IndoorMapController:
    def __init__(self, osmm):
        self.univis_c = UnivISRoomController()
        self.indoor_cc = IndoorMapperConfigController()
        self.graph_buildings = None
        self.osmm = osmm

    def add_buildings_to_graph(self, buildings: List[GraphBuilding]):
        for building in buildings:
            building.add_staircase_edges()

    def get_graph_buildings(self, buildings: List[Building]) -> List[GraphBuilding]:
        return [GraphBuilding(self.osmm, building, self._get_graph_stair_cases(building)) for building in buildings]

    def _get_graph_stair_cases(self, building) -> List[GraphStairCase]:
        return [GraphStairCase(staircase, self.osmm.add_osm_node(staircase.coord), self._get_graph_entries(staircase))
                for staircase in building.staircases]

    def _get_graph_entries(self, staircase) -> List[GraphBuildingEntryPoint]:
        return [GraphBuildingEntryPoint(entry, self.osmm) for entry in staircase.entries]

    def add_staircase_edges(self, staircase: GraphStairCase):
        edges = len(self.osmm.graph.edges)
        for entry in staircase.graph_entries:
            if not entry.is_blocked():
                self.osmm.add_osm_edge(staircase.position_id, entry.nearest_graph_node_id)
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
