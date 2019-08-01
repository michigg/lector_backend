from typing import List

import requests
import xmltodict
import os
import json

import logging

logger = logging.getLogger(__name__)


class Room:
    def __init__(self, univis_room):
        self.building_key = None
        self.number = None
        self.level = None
        self._init_room_number(univis_room)

    def _init_room_number(self, univis_room):
        splitted_room_id = str(univis_room['short']).split('/')
        splitted_room_number = splitted_room_id[1].split('.')
        self.building_key = splitted_room_id[0]
        self.level = int(splitted_room_number[0])
        self.number = int(splitted_room_number[1])

    def __str__(self):
        return f'{self.building_key}/{self.level:02d}.{self.number:03d}'


class Floor:
    def __init__(self, level, room_range_min, room_range_max):
        self.level = level
        self.room_range_min = room_range_min
        self.room_range_max = room_range_max


class StairCase:
    def __init__(self, name, floors: List[Floor]):
        self.name = name
        self.floors = floors
        self.rooms = []

    def add_room(self, room: Room):
        # TODO: better insert sort
        self.rooms.append(room)
        self.rooms.sort(key=lambda x: x.number)

    def __str__(self):
        output = f'Staircase {self.name}\n'
        for room in self.rooms:
            output += f'{room}, '
        return output


class Building:
    def __init__(self, key, staircases: List[StairCase]):
        self.key = key
        self.staircases = staircases

    def __str__(self):
        output = f'Building {self.key}\n'
        for staircase in self.staircases:
            output += f'{staircase}\n'
        return output


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
                staircase_objs.append(StairCase(staircase['name'], floor_objs))
            building_objs.append(Building(building['building_id'], staircase_objs))
        return building_objs


class UnivISRoomController:
    def __init__(self):
        self.univis_api_base_url = "http://univis.uni-bamberg.de/prg"

    def _get_univis_api_url(self, building_key):
        return f'{self.univis_api_base_url}?search=rooms&name={building_key}&show=xml'

    def loadPage(self, url: str):
        return xmltodict.parse(requests.get(url).content)

    def get_rooms(self, data: dict, building_key: str) -> List[Room]:
        rooms = []
        for room in data['UnivIS']['Room']:
            if str(f'{building_key}/').lower() in room['short'].lower():
                rooms.append(Room(room))
        return rooms

    def getPersons(self, data: dict):
        persons = []
        for person in data['UnivIS']['Person']:
            persons.append(person)
        return persons

    def parsePage(self, url):
        page = self.loadPage(url)
        data = xmltodict.parse(page)
        rooms = self.get_rooms(data)
        return rooms

    def get_rooms_by_building_key(self, building_key) -> List[Room]:
        data = self.loadPage(self._get_univis_api_url(building_key))
        return self.get_rooms(data, building_key)


class IndoorMapController:
    def __init__(self):
        self.univis_api_base_url = "http://univis.uni-bamberg.de/prg"

    def load_indoor_map_data(self):
        univis_c = UnivISRoomController()
        indoor_cc = IndoorMapperConfigController()
        for building in indoor_cc.buildings:
            rooms = univis_c.get_rooms_by_building_key(building.key)
            for staircase in building.staircases:
                for floor in staircase.floors:
                    for room in rooms:
                        if room.level == floor.level and floor.room_range_min <= room.number <= floor.room_range_max:
                            staircase.add_room(room)
                            rooms.pop()

        for building in indoor_cc.buildings:
            print(building)
