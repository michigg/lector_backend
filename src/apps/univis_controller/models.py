import logging
from enum import Enum
from typing import List

# Create your models here.
from django.utils import timezone

from apps.building_controller.models import Room

logger = logging.getLogger(__name__)


class UnivISRoom(Room):
    def __init__(self, univis_room):
        building_key, level, number = self._init_room_number(univis_room)
        Room.__init__(self, building_key, level, number)
        self.univis_key = univis_room['@key']

    @staticmethod
    def _init_room_number(univis_room) -> (str, int, int):
        splitted_room_id = str(univis_room['short']).split('/')
        splitted_room_number = splitted_room_id[1].split('.')
        building_key = splitted_room_id[0]
        level = int(splitted_room_number[0])
        number = int(splitted_room_number[1])
        return building_key, level, number

    def __str__(self):
        return f'{self.building_key}/{self.level:02d}.{self.number:03d}'


class LectureType(Enum):
    EXERCISE = "Übung"
    TUTORIUM = "Tutorium"
    LECTURE = "Vorlesung"
    SEMINAR = "Seminar"
    FURTHER_LECTURE = "Sonstige Lehrveranstaltung"
    SEMINAR_PRO_SEMINAR = "Seminar/Proseminar"
    PRO_SEMINAR_EXERCISE = "Proseminar/Übung"
    PRO_SEMINAR = "Proseminar"
    LECTURE_SEMINAR = "Vorlesung/Seminar"
    SEMINAR_EXERCISE = "Seminar/Übung"
    BASIC_COURSE = "Grundkurs"
    SOURCE_STUDY_EXERCISE = "Quellenkundliche Übung"
    PRO_SEMINAR_MAIN_SEMINAR = "Proseminar/Hauptseminar"
    SEMINAR_PRO_SEMINAR_EXERCISE = "Seminar/Proseminar/Übung"
    LECTURE_EXERCISE = "Vorlesung/Übung"
    EXERCISE_TUTORIUM = "Übung/Tutorium"
    BLOCK_SEMINAR = "Blockseminar"
    EXERCISE_BLOCK_SEMINAR = "Übung/Blockseminar"
    MAIN_SEMINAR = "Hauptseminar"
    COURSE = "Kurs"
    LANGUAGE_TRAINING = "Sprachpraktische Ausbildung"
    LECTURE_WITH_STUDYACCOMPANYING_EXAMINATION = "Vorlesung mit studienbegleitender Prüfung"
    TERRAIN_SEMINAR = "Geländeseminar"
    PROJECT = "Project"
    PRAKTIKUM_EXERCISE = "Praktikum / Übung"


class LectureTerm:
    def __init__(self, univis_term: dict, rooms: List[UnivISRoom]):
        self.starttime = timezone.datetime.strptime(univis_term.get('starttime'), '%H:%M')
        self.endtime = timezone.datetime.strptime(univis_term.get('endtime'), '%H:%M')
        self.repeat = univis_term.get('repeat')
        self.room = rooms


class Lecture:
    def __init__(self, univis_lecture: dict, rooms: List[UnivISRoom]):
        terms = [term[1] for term in list(univis_lecture['terms'].items())][0]
        terms = [dict(term) for term in terms] if type(terms) is list else [dict(terms)]
        dozs = []
        if 'dozs' in univis_lecture:
            dozs = [doz[1] for doz in list(univis_lecture['dozs'].items())][0]
            dozs = [dict(doz['UnivISRef']) for doz in dozs] if type(dozs) is list else [dict(dozs['UnivISRef'])]

        self.univis_key = univis_lecture.get('@key')
        self._init_lecture_terms(rooms, terms)
        self.type = self._get_type(univis_lecture.get('type'))
        self.lecturers = [Person(lecturer) for lecturer in dozs]
        self.name = univis_lecture.get('name')
        self.orgname = univis_lecture.get('orgname')
        self.parent_lecture__ref = univis_lecture['parent-lv']['UnivISRef']['@key'] if univis_lecture.get('parent-lv',
                                                                                                          None) else None
        self.parent_lecture = None

    def _init_lecture_terms(self, rooms, terms):
        lecture_terms = []
        for term in terms:
            if 'room' in term:
                rooms = list(filter(lambda x: x.univis_key == dict(term['room']['UnivISRef']).get('@key'), rooms))
                if rooms:
                    lecture_terms.append(LectureTerm(term, rooms[0]))
        self.terms = lecture_terms

    @staticmethod
    def _get_type(univis_type: str) -> LectureType or None:
        types = {'V': LectureType.LECTURE, 'Ü': LectureType.EXERCISE, 'TU': LectureType.TUTORIUM,
                 'S': LectureType.SEMINAR, 'SL': LectureType.FURTHER_LECTURE, 'S/PS': LectureType.SEMINAR_PRO_SEMINAR,
                 'PS/Ü': LectureType.PRO_SEMINAR_EXERCISE, 'PS': LectureType.PRO_SEMINAR,
                 'V/S': LectureType.LECTURE_SEMINAR, 'S/Ü': LectureType.SEMINAR_EXERCISE,
                 'GK': LectureType.BASIC_COURSE, 'Q/Ü': LectureType.SOURCE_STUDY_EXERCISE,
                 'PS/HS': LectureType.PRO_SEMINAR_MAIN_SEMINAR, 'S/PS/Ü': LectureType.SEMINAR_PRO_SEMINAR_EXERCISE,
                 'V/Ü': LectureType.LECTURE_EXERCISE, 'Ü/T': LectureType.EXERCISE_TUTORIUM,
                 'BS': LectureType.BLOCK_SEMINAR, 'Ü/BS': LectureType.EXERCISE_BLOCK_SEMINAR,
                 'HS': LectureType.MAIN_SEMINAR, 'K': LectureType.COURSE, 'SA': LectureType.LANGUAGE_TRAINING,
                 'V/SP': LectureType.LECTURE_WITH_STUDYACCOMPANYING_EXAMINATION, 'GS': LectureType.TERRAIN_SEMINAR,
                 'PROJ': LectureType.PROJECT, 'PUE': LectureType.PRAKTIKUM_EXERCISE}

        return types[univis_type] if univis_type in types else None

    def get_first_term(self) -> List[LectureTerm] or None:
        sorted_terms = self._get_sorted_terms()
        return sorted_terms[0] if len(sorted_terms) > 0 else None

    def get_last_term(self) -> List[LectureTerm] or None:
        sorted_terms = self._get_sorted_terms()
        return sorted_terms[-1] if len(sorted_terms) > 0 else None

    def _get_sorted_terms(self) -> List[LectureTerm]:
        return sorted(self.terms, key=lambda x: x.starttime)

    def get_rooms(self):
        return [term.room for term in self.terms]

    def __str__(self):
        if self.parent_lecture:
            return f'Lecture {self.name}:\n\tUnivIS Key: {self.univis_key}\n\tType: {self.type}\n\tOrgname: {self.orgname}\n\tParent Lecture: {self.parent_lecture.name}\n\tROOMS: {self.get_rooms()}'
        else:
            return f'Lecture {self.name}:\n\tUnivIS Key: {self.univis_key}\n\tType: {self.type}\n\tOrgname: {self.orgname}\n\tParent Lecture Ref: {self.parent_lecture__ref}\n\tROOMS: {self.get_rooms()}'


class Person:
    def __init__(self, univis_person: dict):
        self.univis_key = univis_person.get('@key')
        self.title = univis_person.get('atitle', None)
        self.first_name = univis_person.get('firstname')
        self.last_name = univis_person.get('lastname')
        self.gender = univis_person.get('gender')
        self.id = univis_person.get('id')
        self.pub_visible = True if univis_person.get('pub_visible', "nein") == "ja" else False
        self.visible = True if univis_person.get('visible', "nein") == "ja" else False

    def __str__(self):
        return f'Person {self.first_name} {self.last_name}\n\tUnivis Key {self.univis_key}\n\tTitle {self.title}\n\tGender {self.gender}'
