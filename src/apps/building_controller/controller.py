import logging
from typing import List

from apps.building_controller.config_controller import BuildingConfigController
from apps.building_controller.graph_models import GraphStairCase, GraphBuilding, GraphBuildingEntryPoint
from apps.building_controller.models import StairCase, Building, Room

logger = logging.getLogger(__name__)


class GraphBuildingController:
    """
    Control the Building to BuildingGraph operations
    """

    def __init__(self, osmm, building_cc=BuildingConfigController()):
        self.building_cc = building_cc
        self.graph_buildings = None
        self.osmm = osmm

    @staticmethod
    def add_buildings_to_graph(buildings: List[GraphBuilding]):
        """
        Add building graphs to the main graph
        :param buildings: buildings that shall be inserted
        """
        for building in buildings:
            logger.info(f'ADD Building {building.key} to graph')
            building.add_staircase_edges()

    def get_graph_buildings(self, buildings: List[Building]) -> List[GraphBuilding]:
        return [GraphBuilding(self.osmm, building, self._get_graph_stair_cases(building)) for building in buildings]

    def _get_graph_stair_cases(self, building: Building) -> List[GraphStairCase]:
        return [GraphStairCase(staircase, self.osmm.add_osm_node(staircase.coord), self._get_graph_entries(staircase))
                for staircase in building.staircases]

    def _get_graph_entries(self, staircase: StairCase) -> List[GraphBuildingEntryPoint]:
        return [GraphBuildingEntryPoint(entry, self.osmm) for entry in staircase.entries]


class BuildingController:
    """
    Offers Room dependend building options
    """

    def __init__(self):
        self.indoor_cc = BuildingConfigController()

    def get_rooms_staircase(self, room: Room, wheelchair=False) -> StairCase or None:
        """
        return the staircase that is used for the given room.
        :param room: room which staircase shall be found
        :param wheelchair:
        :return: the rooms staircase
        """
        building = self.get_rooms_building(room)
        return building.get_rooms_staircase(room) if building else None

    def get_rooms_building(self, room: Room, wheelchair=False) -> Building or None:
        """
        return the building that includes the given room
        :param room: room which building shall be found
        :param wheelchair:
        :return: the rooms building
        """
        for building in self.indoor_cc.buildings:
            if str(building.key).lower() == str(room.building_key).lower():
                return building
        return None
