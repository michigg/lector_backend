import logging
from typing import List

from building_controller.utils.building_models import GraphStairCase, GraphBuilding, StairCase, Building, Room
from building_controller.utils.config_controller import IndoorMapperConfigController
from lector.utils.open_space_models import GraphBuildingEntryPoint

logger = logging.getLogger(__name__)


class IndoorMapController:
    def __init__(self, osmm):
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


class RoomStaircaseController:
    def __init__(self):
        self.indoor_cc = IndoorMapperConfigController()

    def get_rooms_staircase(self, room: Room, wheelchair=False) -> StairCase or None:
        for building in self.indoor_cc.buildings:
            # TODO: Add wheelchair option
            if str(building.key).lower() == str(room.building_key).lower():
                return building.get_rooms_staircase(room)
        return None
