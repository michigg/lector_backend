import logging

from django.core.management.base import BaseCommand

from lecture_room_service.utils.univis_lecture_controller import UnivISLectureController


class Command(BaseCommand):
    help = 'Load indoor map configs and match univis roomsx'

    def add_arguments(self, parser):
        parser.add_argument('lecture_name', type=str)

    def handle(self, *args, **options):
        logger = logging.getLogger('')
        logger.setLevel(logging.INFO)
        univis_lecture_c = UnivISLectureController()
        lectures = univis_lecture_c.get_lectures_by_token(options.get('lecture_name'))
        for lecture in lectures:
            print(lecture.__dict__)

        logger.setLevel(logging.WARNING)
