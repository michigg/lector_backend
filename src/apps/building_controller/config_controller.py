import json
import logging
import os
from datetime import datetime
from typing import List

from apps.building_controller.models import Building, Floor, StairCase, BuildingEntryPoint

logger = logging.getLogger(__name__)


class BuildingConfigController:
    def __init__(self, config_dir='/configs/indoor_maps'):
        self.config_dir = config_dir
        self.buildings = self.get_buildings()
        logger.info(f'LOADED BUILDINGS {len(self.buildings)}')

    def get_building_config(self, file='WE5.json'):
        with open(f'{self.config_dir}/{file}') as f:
            return json.load(f)

    def get_building_config_files(self):
        return [f for f in os.listdir(self.config_dir) if f.endswith('.json')]

    def get_buildings(self) -> List[Building]:
        return [self._get_building(self.get_building_config(file)) for file in self.get_building_config_files()]

    def _get_building(self, building: dict):
        return Building(building['building_id'], self._get_staircases(building))

    def _get_staircases(self, building: dict):
        return [self._get_staircase(staircase) for staircase in building['staircases']]

    @staticmethod
    def _get_staircase_floors(staircase: dict):
        return [Floor(floor['level'], floor['ranges']) for floor in staircase['floors']]

    @staticmethod
    def _get_staircase_entry_points(staircase: dict):
        return [BuildingEntryPoint(entry) for entry in staircase['entries']]

    @staticmethod
    def _get_staircase_coord(staircase: dict):
        return staircase['coord']

    @staticmethod
    def _get_staircase_name(staircase: dict):
        return staircase['name']

    @staticmethod
    def _get_staircase_blocked_date(staircase: dict) -> datetime or None:
        if "blocked" in staircase:
            return datetime.strptime(staircase['blocked'], "%Y-%m-%d")
        return None

    def _get_staircase_neigbours(self, staircase: dict):
        return staircase.get("neighbours", None)

    def _get_staircase_wheelchair(self, staircase: dict):
        return staircase.get("wheelchair", False)

    def _get_staircase_id(self, staircase: dict):
        return staircase.get("id", -1)

    def _get_staircase(self, staircase):
        return StairCase(
            self._get_staircase_id(staircase),
            self._get_staircase_name(staircase),
            self._get_staircase_floors(staircase),
            self._get_staircase_coord(staircase),
            self._get_staircase_entry_points(staircase),
            self._get_staircase_blocked_date(staircase),
            self._get_staircase_neigbours(staircase),
            self._get_staircase_wheelchair(staircase),
        )
