import json
import os
from typing import List

from src.indoor_mapper.utils.building_models import Building, Floor, StairCase
from src.indoor_mapper.utils.indoor_mapper import logger


class IndoorMapperConfigController:
    def __init__(self, config_dir='/indoor_maps'):
        self.config_dir = config_dir
        self.buildings = self._get_buildings()
        logger.info(f'LOADED BUILDINGS {len(self.buildings)}')

    def _load_building_config(self, file='erba.json'):
        logger.info(f'LOAD config of file {self.config_dir}/{file}')
        with open(f'{self.config_dir}/{file}') as f:
            return json.load(f)

    def _get_build_config_files(self):
        return [f for f in os.listdir(self.config_dir) if f.endswith('.json')]

    def _get_buildings(self) -> List[Building]:
        building_objs = []
        for file in self._get_build_config_files():
            building = self._load_building_config(file)
            staircase_objs = []
            for staircase in building['staircases']:
                floor_objs = []
                for floor in staircase['floors']:
                    floor_objs.append(Floor(floor['level'], floor['room_range_min'], floor['room_range_max']))
                staircase_objs.append(
                    StairCase(staircase['name'], floor_objs, staircase['coord'], staircase['entries']))
            building_objs.append(Building(building['building_id'], staircase_objs))
        return building_objs