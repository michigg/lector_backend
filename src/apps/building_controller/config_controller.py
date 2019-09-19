import json
import logging
import os
from datetime import datetime
from json import JSONDecodeError
from typing import List

from django.conf import settings

from apps.building_controller.models import Building, Floor, StairCase, BuildingEntryPoint

logger = logging.getLogger(__name__)


class BuildingConfigController:
    def __init__(self, config_dir=settings.BUILDINGS_CONFIG_DIR):
        self.config_dir = config_dir
        self.buildings = self.get_buildings()
        logger.info(f'LOADED BUILDINGS {len(self.buildings)}')

    def get_building_config(self, file):
        logger.info(f'LOAD json of file {self.config_dir}/{file}')
        try:
            with open(f'{self.config_dir}/{file}') as f:
                try:
                    return json.load(f)
                except JSONDecodeError as e:
                    logger.warn(f"Could not Load json {f.name}")
                    return None
        except FileNotFoundError as e:
            logger.warn(f"Could not find json")
            return None

    def get_building_config_files(self) -> List:
        return [f for f in os.listdir(self.config_dir) if f.endswith('.json')]

    def get_buildings(self) -> List[Building]:
        buildings = []
        for file in self.get_building_config_files():
            building_config = self.get_building_config(file)
            building = self._get_building(building_config) if building_config else None
            if building:
                buildings.append(building)
        return buildings

    def _get_building(self, building: dict) -> Building:
        return Building(building['building_id'], self._get_staircases(building))

    def _get_staircases(self, building: dict) -> List[StairCase]:
        return [self._get_staircase(staircase) for staircase in building['staircases']]

    @staticmethod
    def _get_staircase_floors(staircase: dict) -> List[Floor]:
        return [Floor(floor['level'], floor['ranges']) for floor in staircase['floors']]

    @staticmethod
    def _get_staircase_entry_points(staircase: dict) -> List[BuildingEntryPoint]:
        return [BuildingEntryPoint(entry) for entry in staircase['entries']]

    @staticmethod
    def _get_staircase_coord(staircase: dict) -> List[float]:
        return staircase['coord']

    @staticmethod
    def _get_staircase_name(staircase: dict) -> str:
        return staircase['name']

    @staticmethod
    def _get_staircase_blocked_date(staircase: dict) -> datetime or None:
        if "blocked" in staircase:
            return datetime.strptime(staircase['blocked'], "%Y-%m-%d")
        return None

    def _get_staircase_neigbours(self, staircase: dict) -> List[int] or None:
        return staircase.get("neighbours", None)

    def _get_staircase_wheelchair(self, staircase: dict) -> bool:
        return staircase.get("wheelchair", False)

    def _get_staircase_id(self, staircase: dict) -> int:
        return staircase.get("id", -1)

    def _get_staircase(self, staircase) -> StairCase:
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
