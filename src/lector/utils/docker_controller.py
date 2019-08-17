import re
import shutil

import docker

import logging

logger = logging.getLogger(__name__)


class DockerController:
    @staticmethod
    def get_container_by_service_name(service_name):
        # TODO check multiple container
        client = docker.from_env()
        for container in client.containers.list(all=True):
            pattern = re.compile(f'.*{service_name}.*')
            if pattern.match(container.name):
                return container

    def restart_container_by_service_name(self, service_name):
        container = self.get_container_by_service_name(service_name)

        if container:
            container.restart()


class DockerGraphhopperController(DockerController):
    def __init__(self, graphhopper_service_name, osm_output_dir, osm_output_filename):
        self.graphhopper_service_name = graphhopper_service_name
        self.osm_output_dir = osm_output_dir
        self.osm_output_filename = osm_output_filename

    def clean_graphhopper_restart(self):
        logger.info("Restart Graphhopper Container")
        self._remove_current_graphhopper_data()
        self.restart_container_by_service_name(self.graphhopper_service_name)

    def _remove_current_graphhopper_data(self):
        shutil.rmtree(f'{self.osm_output_dir}/{self.osm_output_filename}-gh', ignore_errors=True)
