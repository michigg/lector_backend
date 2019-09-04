import logging
import re
from pyexpat import ExpatError
from typing import List

import requests
import xmltodict
from django.conf import settings
from django.utils import timezone

from .models import UnivISRoom, Person, Lecture

logger = logging.getLogger(__name__)


class UnivISController:
    def __init__(self):
        self.room_regex = "([a-zA-Z]*[0-9]*)\/([0-9]{2})\.([0-9]{2,3}).*"

    def load_page(self, url: str):
        data = requests.get(url).content
        try:
            return xmltodict.parse(data)
        except ExpatError:
            return None

    def get_persons(self, data: dict) -> List[Person]:
        return [Person(person) for person in data['UnivIS']['Person'] if 'Person' in data['UnivIS']]

    def is_a_room(self, room: dict):
        try:
            return re.match(self.room_regex, room['short'])
        except TypeError:
            return False

    def get_rooms_from_data(self, data: List):
        return [UnivISRoom(room) for room in data if self.is_a_room(room)]


class UnivISLectureController(UnivISController):
    def __init__(self, semester=settings.UNIVIS_SEMESTER):
        UnivISController.__init__(self)
        self.univis_api_base_url = "http://univis.uni-bamberg.de/prg"
        self.semester = semester

    def _get_univis_api_url(self, lecture_search_token):
        return f'{self.univis_api_base_url}?search=lectures&name={lecture_search_token}&sem={self.semester}&show=xml'

    def get_rooms(self, data: dict) -> List[UnivISRoom]:
        rooms = []
        if 'Room' in data['UnivIS']:
            if type(data['UnivIS']['Room']) is list:
                rooms = self.get_rooms_from_data(data['UnivIS']['Room'])
            else:
                rooms = [UnivISRoom(data['UnivIS']['Room'])] if self.is_a_room(data['UnivIS']['Room']) else []
        return rooms

    def get_lectures(self, data: dict, rooms: List[UnivISRoom]) -> List[Lecture]:
        lectures = []
        if 'Lecture' in data['UnivIS']:
            if type(data['UnivIS']['Lecture']) is list:
                lectures = [Lecture(lecture, rooms) for lecture in data['UnivIS']['Lecture'] if 'terms' in lecture]
            else:
                lectures = [Lecture(data['UnivIS']['Lecture'], rooms)]
        return lectures

    def get_univis_key_dict(self, objects):
        map = {}
        for object in objects:
            map[object.univis_key] = object
        return map

    def get_lectures_by_token(self, token: str):
        data = self.load_page(self._get_univis_api_url(token))
        if data and 'UnivIS' in data and 'Lecture' in data['UnivIS']:
            lectures = self.get_lectures(data, self.get_rooms(data))
            lecture_map = self.get_univis_key_dict(lectures)
            person_map = self.get_univis_key_dict(self.get_persons(data))
            clean_lectures = []
            for lecture in lectures:
                if len(lecture.terms) > 0:
                    if lecture.parent_lecture__ref:
                        lecture.parent_lecture = lecture_map[lecture.parent_lecture__ref]
                    lecture.lecturers = [person_map[lecturer.univis_key] for lecturer in lecture.lecturers]
                    clean_lectures.append(lecture)

            logger.info(f'FOUND LECTURES {len(clean_lectures)}')
            return clean_lectures
        return []

    def get_lectures_split_by_date(self, lectures):
        current_time = timezone.localtime(timezone.now())
        lectures = self.get_lectures_sorted_by_starttime(lectures)
        lectures_before = []
        lectures_after = []
        for lecture in lectures:
            if lecture.get_last_term().starttime.time() < current_time.time():
                lectures_before.append(lecture)
            else:
                lectures_after.append(lecture)
        return lectures_after, lectures_before

    def get_lectures_sorted_by_starttime(self, lectures):
        return sorted(lectures, key=lambda lecture: lecture.get_first_term().starttime)

    # TODO: Implement child lectures. Currently not used
    # def get_lecture_map_by_univis_id(self, lectures: List[Lecture]):
    #     lecture_map = {}
    #     for lecture in lectures:
    #         lecture_map[lecture.univis_key] = lecture
    #     return lecture_map


class UnivISRoomController(UnivISController):
    def __init__(self):
        UnivISController.__init__(self)
        self.univis_api_base_url = "http://univis.uni-bamberg.de/prg"

    def _get_univis_api_url(self, building_key):
        return f'{self.univis_api_base_url}?search=rooms&name={building_key}&show=xml'

    def get_rooms(self, data: dict) -> List[UnivISRoom]:
        return self.get_rooms_from_data(data['UnivIS']['Room']) if 'Room' in data['UnivIS'] else []

    # def get_building_keys_rooms(self, building_key: str) -> List[UnivISRoom]:
    #     data = self.load_page(self._get_univis_api_url(building_key))
    #     rooms = self.get_rooms_from_data(data['UnivIS']['Room'])
    #     return [room for room in rooms if building_key.lower() in room.building_key.lower()] if 'Room' in data[
    #         'UnivIS'] else []

    def get_tokens_rooms(self, token) -> List[UnivISRoom]:
        data = self.load_page(self._get_univis_api_url(token))
        return self.get_rooms(data) if data else []
