import json
import os
import logging
from typing import List

# from .open_space_controller import OpenSpace, EntryPoint
from lector.utils.open_space_models import EntryPoint, OpenSpace

logger = logging.getLogger(__name__)


class OpenSpaceConfigController:
    def __init__(self, config_dir='/open_spaces'):
        self.config_dir = config_dir
        self.open_spaces = self._load_open_spaces()
        logger.info(f'LOADED OPEN SPACES {len(self.open_spaces)}')

    def _load_geojson(self, file='markusplatz.geojson'):
        logger.info(f'LOAD geojson of file {self.config_dir}/{file}')
        with open(f'{self.config_dir}/{file}') as f:
            return json.load(f)

    def _get_geojson_files(self):
        return [f for f in os.listdir(self.config_dir) if f.endswith('.geojson') or f.endswith('.json')]

    def _get_geojsons(self):
        files = self._get_geojson_files()
        logger.info(f'FOUND {len(files)} geojsons')
        return [self._load_geojson(file) for file in files]

    def _get_open_space(self, geojson) -> OpenSpace:
        walkables = []
        restricted = []
        entry_points = []
        for feature in geojson['features']:
            if "walkable" in feature['properties']:
                if feature['properties']['walkable'] == 'True':
                    walkables.append(feature['geometry']['coordinates'][0])
                else:
                    restricted.append(feature['geometry']['coordinates'][0])
            if "entry" in feature['properties'] and feature['properties']['entry'] == "True":
                entry_points.append(EntryPoint(feature['geometry']['coordinates']))
        if len(walkables) > 1:
            logger.warn(f'Multiple walkable areas detected. Only one walkable area for each config file is allowed!')
        if len(walkables) == 0:
            logger.error(f'No walkable area found! Area dismissed!')
            return OpenSpace()
        else:
            return OpenSpace(walkables[0], restricted, entry_points)

    def _load_open_spaces(self):
        return [self._get_open_space(geojson) for geojson in self._get_geojsons()]

    def get_open_spaces(self) -> List[OpenSpace]:
        return self.open_spaces
