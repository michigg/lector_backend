from typing import List

import requests
import xmltodict

from indoor_mapper.utils.univis_models import Room


class UnivISRoomController:
    def __init__(self):
        self.univis_api_base_url = "http://univis.uni-bamberg.de/prg"

    def _get_univis_api_url(self, building_key):
        return f'{self.univis_api_base_url}?search=rooms&name={building_key}&show=xml'

    @staticmethod
    def loadPage(url: str):
        return xmltodict.parse(requests.get(url).content)

    @staticmethod
    def get_rooms_with_same_key(data: dict, key: str) -> List[Room]:
        if 'Room' not in data['UnivIS']:
            return []
        return [Room(room) for room in data['UnivIS']['Room'] if str(f'{key}/').lower() in room['short'].lower()]

    def get_rooms(self, data: dict) -> List[Room]:
        if 'Room' not in data['UnivIS']:
            return []
        return [Room(room) for room in data['UnivIS']['Room'] if not self.is_a_room_group(room)]

    def is_a_room_group(self, room: dict):
        room_group_indicators = ['Raumgruppe', 'PR_']
        for indicator in room_group_indicators:
            if indicator.lower() in room['short'].lower():
                return True
        return False

    @staticmethod
    def get_persons(data: dict):
        # TODO change to Person class
        return [person for person in data['UnivIS']['Person']]

    def get_rooms_by_building_key(self, building_key) -> List[Room]:
        data = self.loadPage(self._get_univis_api_url(building_key))
        return self.get_rooms_with_same_key(data, building_key)

    def get_rooms_by_token(self, token) -> List[Room]:
        data = self.loadPage(self._get_univis_api_url(token))
        return self.get_rooms(data)
