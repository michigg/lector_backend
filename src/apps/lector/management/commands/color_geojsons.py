import logging

from django.core.management.base import BaseCommand

from apps.docker_controller.controllers import DockerGraphhopperController
from apps.lector.controllers import OSMController
from apps.open_space_controller.config_controller import OpenSpaceConfigController

SERVICE_NAME = 'graphhopper'
OSM_OUTPUT_DIR = '/osm_data'
OSM_OUTPUT_FILENAME = 'data'


class Command(BaseCommand):
    help = 'Colors all geojson files'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        open_space_cc = OpenSpaceConfigController()
        open_space_cc.set_open_space_colors()
