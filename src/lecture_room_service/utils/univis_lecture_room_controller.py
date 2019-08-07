from typing import List

import requests
import xmltodict
from django.utils import timezone

from lecture_room_service.utils.univis_models import Room, Lecture, Person


class UnivISLectureController:
    def __init__(self):
        self.univis_api_base_url = "http://univis.uni-bamberg.de/prg"
        self.semester = "2019s"

    def _get_univis_api_url(self, lecture_search_token):
        return f'{self.univis_api_base_url}?search=lectures&name={lecture_search_token}&sem={self.semester}&show=xml'

    def load_page(self, url: str):
        return xmltodict.parse(requests.get(url).content)

    def get_rooms(self, data: dict) -> List[Room]:
        rooms = []
        if type(data['UnivIS']['Room']) is list:
            for room in data['UnivIS']['Room']:
                rooms.append(Room(room))
        else:
            rooms.append(Room(data['UnivIS']['Room']))
        return rooms

    def get_persons(self, data: dict) -> List[Person]:
        persons = []
        for person in data['UnivIS']['Person']:
            persons.append(Person(person))
        return persons

    def get_lectures(self, data: dict, rooms: List[Room]) -> List[Lecture]:
        lectures = []
        if type(data['UnivIS']['Lecture']) is list:
            for lecture in data['UnivIS']['Lecture']:
                if 'terms' in lecture:
                    lectures.append(Lecture(lecture, rooms))
        else:
            lectures.append(Lecture(data['UnivIS']['Lecture'], rooms))
        return lectures

    def get_univis_key_dict(self, objects):
        map = {}
        for object in objects:
            map[object.univis_key] = object
        return map

    def get_lectures_by_token(self, token: str):
        data = self.load_page(self._get_univis_api_url(token))
        rooms = self.get_rooms(data)
        persons = self.get_persons(data)
        lectures = self.get_lectures(data, rooms)
        lecture_map = self.get_univis_key_dict(lectures)
        person_map = self.get_univis_key_dict(persons)
        clean_lectures = []
        for lecture in lectures:
            if len(lecture.terms) > 0:
                if lecture.parent_lecture__ref:
                    lecture.parent_lecture = lecture_map[lecture.parent_lecture__ref]
                new_lecturers = []
                for lecturer in lecture.lecturers:
                    new_lecturers.append(person_map[lecturer.univis_key])
                lecture.lecturers = new_lecturers
                clean_lectures.append(lecture)

        for lecture in clean_lectures:
            print(lecture)
        print(f'FOUND LECTURES {len(clean_lectures)}')
        return clean_lectures

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
