import json
import logging
import os
from json import JSONDecodeError
from typing import List

from django.conf import settings

from apps.lector.models import EntryPoint
from .models import OpenSpace

logger = logging.getLogger(__name__)
RESTRICTED_TYPE = "RESTRICTED"
WALKABLE_TYPE = "WALKABLE"
BLOCKED_TYPE = "BLOCKED"
ENTRY_TYPE = "ENTRY"


class OpenSpaceConfigController:
    """
    Controll the Open Space config files
    """

    def __init__(self, config_dir=settings.OPEN_SPACES_CONFIG_DIR):
        self.config_dir = config_dir
        self.open_spaces = self._load_open_spaces()
        logger.info(f'LOADED OPEN SPACES {len(self.open_spaces)}')

    def load_geojson(self, file) -> dict or None:
        logger.info(f'LOAD geojson of file {self.config_dir}/{file}')
        try:
            with open(f'{self.config_dir}/{file}') as f:
                try:
                    geojson = json.load(f)
                    return {'file_name': file, 'geojson': geojson}
                except JSONDecodeError as e:
                    logger.warn(f"Could not Load json {f.name}")
                    return None
        except FileNotFoundError as e:
            logger.warn(f"Could not Find json")
            return None

    def get_open_spaces_files(self) -> List:
        return [f for f in os.listdir(self.config_dir) if f.endswith('.geojson') or f.endswith('.json')]

    def _get_geojsons(self) -> List[dict]:
        files = self.get_open_spaces_files()
        logger.info(f'FOUND {len(files)} geojsons')
        geojsons = []
        for file in files:
            geojson = self.load_geojson(file)
            if geojson:
                geojsons.append(geojson)
        return geojsons

    def _load_open_space(self, data: dict) -> OpenSpace or None:
        """Check config and load the json file to an OpenSpace instance"""
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
            return None
        if len(walkables) == 0:
            logger.error(f'No walkable area found! Area dismissed!')
            return None
        return OpenSpace(data['file_name'], walkables[0], restricted, blocked, entry_points)

    def _load_open_spaces(self) -> List[OpenSpace]:
        open_spaces = []
        for geojson in self._get_geojsons():
            open_space = self._load_open_space(geojson)
            if open_space:
                open_spaces.append(open_space)
        return open_spaces

    def get_open_space(self, file_name: str) -> OpenSpace or None:
        for open_space in self.open_spaces:
            if open_space.file_name == file_name:
                return open_space
        return None

    def get_open_spaces(self) -> List[OpenSpace]:
        return self.open_spaces

    def set_open_space_colors(self):
        for file in self.get_open_spaces_files():
            geojson = self.get_colored_geojson(file)
            with open(f'{self.config_dir}/{file}', 'w') as f:
                json.dump(geojson['geojson'], f)

    def get_colored_geojson(self, file) -> dict:
        """Coloring a open space config file. Returns colored geojson"""
        geojson = self.load_geojson(file)
        for feature in geojson['geojson']['features']:
            polygon = feature['geometry']['coordinates'][0]
            if "type" in feature['properties']:
                type = feature['properties']['type'].lower()
                if type == WALKABLE_TYPE.lower():
                    feature['properties']['fill'] = "#0eae00"
                    feature['properties']['fill-opacity'] = 0.2
                if type == RESTRICTED_TYPE.lower():
                    feature['properties']['fill'] = "#e6b34e"
                if type == BLOCKED_TYPE.lower():
                    feature['properties']['fill'] = "#d52d2d"
        return geojson
