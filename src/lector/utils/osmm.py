import osmnx as ox
import docker
import re

BAMBERG_BBOX = [49.865874134216426, 49.925145775384436, 10.836982727050781, 10.951995849609375]
SERVICE_NAME = 'graphhopper'


def download_map():
    G = ox.graph_from_bbox(49.925145775384436, 49.865874134216426, 10.951995849609375, 10.836982727050781,
                           network_type='all')
    ox.save_graph_osm(G, filename='bamberg.osm', folder='/osm_data')
    restart_container_by_service_name(SERVICE_NAME)


def get_container_by_service_name(name):
    # TODO check multiple container
    client = docker.from_env()
    for container in client.containers.list():
        pattern = re.compile(f'.*{name}.*')
        if pattern.match(container.name):
            return container


def restart_container_by_service_name(container_name):
    container = get_container_by_service_name(container_name)
    container.restart()
