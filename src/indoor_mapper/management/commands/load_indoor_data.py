import logging

from django.core.management.base import BaseCommand
from indoor_mapper.utils.indoor_mapper import IndoorMapController


class Command(BaseCommand):
    help = 'Load indoor map configs and match univis roomsx'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        logger = logging.getLogger('')
        logger.setLevel(logging.INFO)
        indoor_map_c = IndoorMapController()
        indoor_map_c.load_indoor_map_data()

        logger.setLevel(logging.WARNING)
