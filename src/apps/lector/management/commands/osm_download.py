import logging

from django.core.management.base import BaseCommand

from apps.docker_controller.controllers import DockerGraphhopperController
from apps.lector.controllers import OSMController
from apps.open_space_controller.models import BBox

SERVICE_NAME = 'graphhopper'
OSM_OUTPUT_DIR = '/osm_data'
OSM_OUTPUT_FILENAME = 'data'


class Command(BaseCommand):
    help = 'Collect osm data from the given bounding box'

    def add_arguments(self, parser):
        parser.add_argument('bbox', nargs='+', type=float,
                            help="Format bbox max_lat: float, min_lat: float, max_lon: float, min_lon: float,\n e.g. BAMBERG_BBOX: [49.925145775384436, 49.865874134216426, 10.951995849609375, 10.836982727050781]")
        parser.add_argument('-r','--gh-restart', action='store_true',
                            help="Saves the Graph in graphhopper and restart the gh container")

    def handle(self, *args, **options):
        logger = logging.getLogger('')
        logger.setLevel(logging.INFO)

        bbox = options['bbox']
        gh_restart = options.get('--gh-restart', False)
        if bbox and len(bbox) != 4:
            self.stdout.write(self.style.ERROR(f'ERROR a bbox should have 4 entries got {len(bbox)}'))
        else:
            osmm = OSMController()
            osmm.create_bbox_open_spaces_plot(BBox(*bbox)) if bbox else osmm.create_bbox_open_spaces_plot()
            osmm.plot_graph()

            if gh_restart:
                osmm.save_graph()

                gh_docker_controller = DockerGraphhopperController(graphhopper_service_name=SERVICE_NAME,
                                                                   osm_output_dir=OSM_OUTPUT_DIR,
                                                                   osm_output_filename=OSM_OUTPUT_FILENAME)
                gh_docker_controller.clean_graphhopper_restart()
            logger.setLevel(logging.WARNING)
