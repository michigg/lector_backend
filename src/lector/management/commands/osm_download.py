import logging

from django.core.management.base import BaseCommand

from lector.utils.docker_controller import DockerGraphhopperController
from lector.utils.osmm import OSMManipulator

SERVICE_NAME = 'graphhopper'
OSM_OUTPUT_DIR = '/osm_data'
OSM_OUTPUT_FILENAME = 'data'


class Command(BaseCommand):
    help = 'Collect osm data from the given bounding box'

    def add_arguments(self, parser):
        # TODO add bounding box
        pass

    def handle(self, *args, **options):
        logger = logging.getLogger('')
        logger.setLevel(logging.INFO)
        osmm = OSMManipulator()
        osmm.add_open_spaces()
        osmm.add_indoor_maps()
        osmm.plot_graph()
        osmm.save_graph()

        gh_docker_controller = DockerGraphhopperController(graphhopper_service_name=SERVICE_NAME,
                                                           osm_output_dir=OSM_OUTPUT_DIR,
                                                           osm_output_filename=OSM_OUTPUT_FILENAME)
        gh_docker_controller.clean_graphhopper_restart()

        logger.setLevel(logging.WARNING)
