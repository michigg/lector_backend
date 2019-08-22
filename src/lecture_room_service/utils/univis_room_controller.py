import logging
import re
from typing import List
from xml.parsers.expat import ExpatError

import requests
import xmltodict

from lecture_room_service.utils.univis_models import UnivISRoom

logger = logging.getLogger(__name__)


class UnivISRoomController:
    def __init__(self):
        self.univis_api_base_url = "http://univis.uni-bamberg.de/prg"

    def _get_univis_api_url(self, building_key):
        return f'{self.univis_api_base_url}?search=rooms&name={building_key}&show=xml'

    @staticmethod
    def loadPage(url: str):
        logger.info(f'Load {url}')
        data = requests.get(url).content
        try:
            return xmltodict.parse(data)
        except ExpatError as err:
            return None

    @staticmethod
    def get_rooms_with_same_key(data: dict, key: str) -> List[UnivISRoom]:
        if 'Room' not in data['UnivIS']:
            return []
        return [UnivISRoom(room) for room in data['UnivIS']['Room'] if str(f'{key}/').lower() in room['short'].lower()]

    def get_rooms_from_data(self, data: List):
        return [UnivISRoom(room) for room in data if self.is_a_room(room)]

    def get_rooms_request(self, data: dict) -> List[UnivISRoom]:
        if 'Room' not in data['UnivIS']:
            return []
        return self.get_rooms_from_data(data['UnivIS']['Room'])

    def is_a_room(self, room: dict):
        try:
            return re.match("([a-zA-Z]*[0-9]*)\/([0-9]{2})\.([0-9]{2,3}).*", room['short'])
        except TypeError:
            return False

    @staticmethod
    def get_persons(data: dict):
        # TODO change to Person class
        return [person for person in data['UnivIS']['Person']]

    def get_rooms_by_building_key(self, building_key) -> List[UnivISRoom]:
        data = self.loadPage(self._get_univis_api_url(building_key))
        return self.get_rooms_with_same_key(data, building_key)

    def get_rooms_by_token(self, token) -> List[UnivISRoom]:
        data = self.loadPage(self._get_univis_api_url(token))
        logger.warn(data)
        if data:
            return self.get_rooms_request(data)
        return []
