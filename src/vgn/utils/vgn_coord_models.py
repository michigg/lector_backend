import json
import logging
import os
from typing import List

logger = logging.getLogger(__name__)


class VGNCoord:
    def __init__(self, location: str, coord: List[float], vgn_url_segment: str, building_key: str):
        self.location = location
        self.coord = coord
        self.vgn_url_segment = vgn_url_segment
        self.building_key = building_key

    def is_coord(self, building_key: str):
        return building_key.lower() == self.building_key.lower()


class VGNCoordConfigController:
    def __init__(self, config_dir='/configs/vgn_coords'):
        self.config_dir = config_dir
        self.vgn_coords = self._load_vgn_coords()
        logger.info(f'LOADED VGNCoords {len(self.vgn_coords)}')

    def load_json(self, file):
        logger.info(f'LOAD json of file {self.config_dir}/{file}')
        with open(f'{self.config_dir}/{file}') as f:
            return {'file_name': file, 'json': json.load(f)}

    def get_vgn_coord_files(self):
        return [f for f in os.listdir(self.config_dir) if f.endswith('.json')]

    def _get_jsons(self):
        files = self.get_vgn_coord_files()
        logger.info(f'FOUND {len(files)} jsons')
        return [self.load_json(file) for file in files]

    def _load_json_vgn_coords(self, data: dict) -> VGNCoord or None:
        vgn_coords = []
        for vgn_coord_raw in data['json']:
            vgn_coords.append(VGNCoord(location=vgn_coord_raw['location'],
                                       coord=[vgn_coord_raw['lon'], vgn_coord_raw['lat']],
                                       vgn_url_segment=vgn_coord_raw['vgn_key'],
                                       building_key=vgn_coord_raw['building_key']))
        return vgn_coords

    def _load_vgn_coords(self):
        vgn_coords = []
        for json in self._get_jsons():
            vgn_coords.extend(self._load_json_vgn_coords(json))
        return vgn_coords


class VGNCoordController:
    def __init__(self):
        self.config = VGNCoordConfigController()

    def get_vgn_coord(self, building_key) -> VGNCoord or None:
        for vgn_coord in self.config.vgn_coords:
            if vgn_coord.is_coord(building_key):
                return vgn_coord
        return None
