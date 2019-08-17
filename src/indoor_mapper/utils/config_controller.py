import json
import logging
import os
from datetime import datetime
from typing import List

from indoor_mapper.utils.building_models import Building, Floor, StairCase
from lector.utils.open_space_models import BuildingEntryPoint

logger = logging.getLogger(__name__)


class IndoorMapperConfigController:
    def __init__(self, config_dir='/configs/indoor_maps'):
        self.config_dir = config_dir
        self.buildings = self.get_buildings()
        logger.info(f'LOADED BUILDINGS {len(self.buildings)}')

    def _load_building_config(self, file='erba.json'):
        logger.info(f'LOAD config of file {self.config_dir}/{file}')
        with open(f'{self.config_dir}/{file}') as f:
            return json.load(f)

    def _get_build_config_files(self):
        return [f for f in os.listdir(self.config_dir) if f.endswith('.json')]

    def get_buildings(self) -> List[Building]:
        return [self._get_building(self._load_building_config(file)) for file in self._get_build_config_files()]

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
    def _get_blocked_date(staircase: dict) -> datetime or None:
        if "blocked" in staircase:
            return datetime.strptime(staircase['blocked'], "%Y-%m-%d")
        return None

    def _get_staircase_neigbours(self, staircase: dict):
        return staircase.get("neighbours", None)

    def _get_staircase(self, staircase):
        return StairCase(self._get_staircase_name(staircase),
                         self._get_staircase_floors(staircase),
                         self._get_staircase_coord(staircase),
                         self._get_staircase_entry_points(staircase),
                         self._get_blocked_date(staircase),
                         self._get_staircase_neigbours(staircase))
