import json
import os


class OpenSpaceConfigController:
    def __init__(self, config_dir='/open_spaces'):
        self.config_dir = config_dir

    def _load_geojson(self, file='markusplatz.geojson'):
        with open(f'{self.config_dir}/{file}') as f:
            return json.load(f)

    def _get_geojson_files(self):
        return [f for f in os.listdir(self.config_dir) if f.endswith('.geojson') or f.endswith('.json')]

    def _get_geojsons(self):
        files = self._get_geojson_files()
        print(f'FOUND FILES:\t{files}')
        return [self._load_geojson(file) for file in files]

    def get_open_space(self, geojson):
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
                entry_points.append(feature['geometry']['coordinates'])
        return {'walkables': walkables, 'restricted': restricted, 'entry_points': entry_points}

    def get_open_spaces(self):
        return [self.get_open_space(geojson) for geojson in self._get_geojsons()]
