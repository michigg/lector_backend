import re
import shutil
import json

import docker
import osmnx as ox

ox.config(log_console=True, use_cache=True)

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
    test_visablity_graph(G)
    plot_graph(G)
    print("GRAPH PLOTTED")
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


def load_geojson():
    with open('/open_spaces/markusplatz.geojson') as f:
        return json.load(f)


def get_polygon_from_geojson():
    return load_geojson()['features'][0]['geometry']['coordinates'][0]


def add_node_as_osm_node(G, node_id, coords):
    G.add_node(node_id, osmid=node_id, x=coords[0], y=coords[1])


def add_osm_edge(G, from_id, to_id):
    G.add_edge(from_id, to_id, attr_dict={'length': 10})


def add_open_space_to_graph(G, coords_dict):
    current_node_id = 0

    origin = coords_dict.pop()
    add_node_as_osm_node(G, current_node_id, origin['coord'])
    nodes = [{'node_id': current_node_id, 'coord': origin['coord'], 'entry_point_id': origin['entry_point_id']}]
    add_osm_edge(G, current_node_id, origin['entry_point_id'])
    current_node_id += 1

    for node in coords_dict:
        add_node_as_osm_node(G, current_node_id, node['coord'])
        add_osm_edge(G, nodes[-1]['node_id'], current_node_id)
        nodes.append({'node_id': current_node_id, 'coord': node['coord'], 'entry_point_id': node['entry_point_id']})
        current_node_id += 1
    return nodes


def add_entry_point_edges(G, nodes):
    for node in nodes:
        add_osm_edge(G, node['node_id'], node['entry_point_id'])


def get_entry_points(G, coords):
    entry_points = []
    for coord in coords:
        point = (coord[1], coord[0])
        node_id, dist = ox.get_nearest_node(G, point, return_dist=True)
        print(dist)
        entry_points.append({'coord': coord, 'entry_point_id': node_id})
    return entry_points


def add_nodes(G, nodes):
    current_node_id = 0
    node_ids = []
    for node in nodes:
        latitude = node[1]
        longitude = node[0]
        # print(G.nodes.data())
        # node, dist = ox.get_nearest_node(G, (latitude, longitude), return_dist=True)
        # print(node, dist)
        G.add_node(current_node_id, osmid=current_node_id, x=longitude, y=latitude)
        # G.add_node(node, osmid=node, x=longitude, y=latitude)
        # print("NODE ADDED")
        # G.add_edge(G, current_node_id, 0)
        # print("EDGE ADDED")
        # print(G.nodes.data())
        node_ids.append(current_node_id)
        current_node_id += 1
    print(G.nodes.data())
    return node_ids


def create_edges_between_all_nodes(G, node_ids):
    for node_id_from in node_ids:
        for node_id_to in node_ids:
            if node_id_from < node_id_to:
                # TODO: distance calculation
                G.add_edge(node_id_from, node_id_to, attr_dict={'length': 10})


def create_visibility_graph(G, polygon_coordinates):
    node_ids = add_nodes(G, polygon_coordinates)
    create_edges_between_all_nodes(G, node_ids)


def test_visablity_graph(G):
    coord_dict = get_entry_points(G, get_polygon_from_geojson())
    nodes = add_open_space_to_graph(G, coord_dict)
    add_entry_point_edges(G, nodes)


if __name__ == '__main__':
    # G = ox.graph_from_address('Bamberg, Oberfranken, Bayern, 96047, Deutschland', network_type='all', distance=500)
    G = ox.graph_from_address('Markusplatz, Bamberg, Oberfranken, Bayern, 96047, Deutschland', network_type='all',
                              distance=300)
    # G = ox.graph_from_bbox(49.925145775384436, 49.865874134216426, 10.951995849609375, 10.836982727050781,
    #                        network_type='all', truncate_by_edge=True)
    # test_visablity_graph(G)
    # coord_dict = get_entry_points(G, get_polygon_from_geojson())
    # nodes = add_open_space_to_graph(G, coord_dict)
    # add_entry_point_edges(G, nodes)

    # print(G.nodes.data())
    # print(G.edges.data())
    nodes = add_nodes(G, get_polygon_from_geojson())
    create_edges_between_all_nodes(G, nodes)
    print("GRAPH LOADED")
    plot_graph(G)
    print("GRAPH PLOTTED")
