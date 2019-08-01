from typing import List

import requests
import xmltodict

from indoor_mapper.utils.univis_models import Room


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

    def get_rooms_by_building_key(self, building_key) -> List[Room]:
        data = self.loadPage(self._get_univis_api_url(building_key))
        return self.get_rooms(data, building_key)
