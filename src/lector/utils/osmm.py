import re
import shutil

import docker
import osmnx as ox

BAMBERG_BBOX = [49.865874134216426, 49.925145775384436, 10.836982727050781, 10.951995849609375]
# BAMBERG_BBOX = [49.9954, 49.7511, 10.7515, 11.1909]
SERVICE_NAME = 'graphhopper'
OSM_OUTPUT_FILENAME = "data"
OSM_OUTPUT_DIR = "/osm_data"


def download_map():
    # G = ox.graph_from_bbox(49.925145775384436, 49.865874134216426, 10.951995849609375, 10.836982727050781,
    #                        network_type='all', truncate_by_edge=True)
    # G = ox.graph_from_address('350 5th Ave, New York, New York', network_type='all')
    # G = ox.graph_from_address('Berlin, 10117, Deutschland', network_type='all')
    # G = ox.graph_from_address('Bamberg, Oberfranken, Bayern, 96047, Deutschland', network_type='all', distance=5000)
    # G = ox.graph_from_address('Erlangen, Mittelfranken, Bayern, 91052, Deutschland', network_type='all')
    G = ox.graph_from_address('Markusplatz, Bamberg, Oberfranken, Bayern, 96047, Deutschland', network_type='all',
                              distance=300)
    ox.save_graph_osm(G, filename=f'{OSM_OUTPUT_FILENAME}.osm', folder=OSM_OUTPUT_DIR)
    remove_current_graphhopper_data()
    restart_container_by_service_name(SERVICE_NAME)


def load_map():
    return ox.graph_from_file(f'{OSM_OUTPUT_DIR}/{OSM_OUTPUT_FILENAME}.osm')


def get_container_by_service_name(name):
    # TODO check multiple container
    client = docker.from_env()
    for container in client.containers.list(all=True):
        pattern = re.compile(f'.*{name}.*')
        if pattern.match(container.name):
            return container


def restart_container_by_service_name(container_name):
    container = get_container_by_service_name(container_name)
    # TODO logging if container is not running
    if container:
        container.restart()


def remove_current_graphhopper_data():
    shutil.rmtree(f'{OSM_OUTPUT_DIR}/{OSM_OUTPUT_FILENAME}-gh', ignore_errors=True)


def plot_graph(G):
    ox.plot_graph(G, save=True, file_format='svg', filename=f'{OSM_OUTPUT_DIR}/network_plot')


if __name__ == '__main__':
    # G = ox.graph_from_address('Bamberg, Oberfranken, Bayern, 96047, Deutschland', network_type='all', distance=500)
    G = ox.graph_from_address('Markusplatz, Bamberg, Oberfranken, Bayern, 96047, Deutschland', network_type='all',
                              distance=300)
    # G = ox.graph_from_bbox(49.925145775384436, 49.865874134216426, 10.951995849609375, 10.836982727050781,
    #                        network_type='all', truncate_by_edge=True)
    print("GRAPH LOADED")
    plot_graph(G)
    print("GRAPH PLOTTED")
