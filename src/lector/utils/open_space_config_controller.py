import json
import os
import logging
from typing import List

# from .open_space_controller import OpenSpace, EntryPoint
from lector.utils.open_space_models import EntryPoint, OpenSpace

logger = logging.getLogger(__name__)

RESTRICTED_TYPE = "RESTRICTED"
WALKABLE_TYPE = "WALKABLE"
BLOCKED_TYPE = "BLOCKED"
ENTRY_TYPE = "ENTRY"


class OpenSpaceConfigController:
    def __init__(self, config_dir='/configs/open_spaces'):
        self.config_dir = config_dir
        self.open_spaces = self._load_open_spaces()
        logger.info(f'LOADED OPEN SPACES {len(self.open_spaces)}')

    def load_geojson(self, file):
        logger.info(f'LOAD geojson of file {self.config_dir}/{file}')
        with open(f'{self.config_dir}/{file}') as f:
            return {'file_name': file, 'geojson': json.load(f)}

    def get_open_spaces_files(self):
        return [f for f in os.listdir(self.config_dir) if f.endswith('.geojson') or f.endswith('.json')]

    def _get_geojsons(self):
        files = self.get_open_spaces_files()
        logger.info(f'FOUND {len(files)} geojsons')
        return [self.load_geojson(file) for file in files]

    def _load_open_space(self, data: dict) -> OpenSpace or None:
        walkables = []
        restricted = []
        blocked = []
        entry_points = []
        for feature in data['geojson']['features']:
            polygon = feature['geometry']['coordinates'][0]
            if "type" in feature['properties']:
                type = feature['properties']['type'].lower()
                if type == WALKABLE_TYPE.lower():
                    walkables.append(polygon)
                if type == RESTRICTED_TYPE.lower():
                    restricted.append(polygon)
                if type == BLOCKED_TYPE.lower():
                    blocked.append(polygon)
                if type == ENTRY_TYPE.lower():
                    entry_points.append(EntryPoint(feature['geometry']['coordinates']))
        if len(walkables) > 1:
            logger.warn(f'Multiple walkable areas detected. Only one walkable area for each config file is allowed!')
        if len(walkables) == 0:
            logger.error(f'No walkable area found! Area dismissed!')
            return None
        return OpenSpace(data['file_name'], walkables[0], restricted, blocked, entry_points)

    def _load_open_spaces(self):
        return [self._load_open_space(geojson) for geojson in self._get_geojsons()]

    def get_open_space(self, file_name: str) -> OpenSpace or None:
        for open_space in self.open_spaces:
            if open_space.file_name == file_name:
                return open_space
        return None

    def get_open_spaces(self) -> List[OpenSpace]:
        return self.open_spaces
