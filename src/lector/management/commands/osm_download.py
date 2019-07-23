from django.core.management.base import BaseCommand
from lector.utils import osmm


class Command(BaseCommand):
    help = 'Collect osm data from the given bounding box'

    def add_arguments(self, parser):
        # TODO add bounding box
        pass

    def handle(self, *args, **options):
        osmm.download_map()
