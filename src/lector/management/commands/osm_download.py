from django.core.management.base import BaseCommand
# from lector.utils.osmm import OSMManipulator
import osmnx as ox


class Command(BaseCommand):
    help = 'Collect osm data from the given bounding box'

    def add_arguments(self, parser):
        # TODO add bounding box
        pass

    def handle(self, *args, **options):
        # osmm.download_map()
        # osmm = OSMManipulator()
        # osmm.test_open_space()
        # map = OSMManipulator.download_map()
        G = ox.graph_from_address('Markusplatz, Bamberg, Oberfranken, Bayern, 96047, Deutschland', network_type='all',
                                  distance=300)
        print(G)
