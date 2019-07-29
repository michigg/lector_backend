import re
import shutil
import json

import docker
import osmnx as ox
import shapely as shply
from pprint import pprint
from shapely.geometry import Polygon, LineString
from shapely.prepared import prep

ox.config(log_console=True, use_cache=True)

BAMBERG_BBOX = [49.865874134216426, 49.925145775384436, 10.836982727050781, 10.951995849609375]
# BAMBERG_BBOX = [49.9954, 49.7511, 10.7515, 11.1909]
SERVICE_NAME = 'graphhopper'
OSM_OUTPUT_FILENAME = "data"
OSM_OUTPUT_DIR = "/osm_data"


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
        # TODO logging if container is not running
        if container:
            container.restart()


class DockerGraphhopperController(DockerController):
    def __init__(self, graphhopper_service_name=SERVICE_NAME, osm_output_dir=OSM_OUTPUT_DIR,
                 osm_output_filename=OSM_OUTPUT_FILENAME):
        self.graphhopper_service_name = graphhopper_service_name
        self.osm_output_dir = osm_output_dir
        self.osm_output_filename = osm_output_filename

    def clean_graphhopper_restart(self):
        self._remove_current_graphhopper_data()
        self.restart_container_by_service_name(self.graphhopper_service_name)

    @staticmethod
    def _remove_current_graphhopper_data():
        shutil.rmtree(f'{OSM_OUTPUT_DIR}/{OSM_OUTPUT_FILENAME}-gh', ignore_errors=True)


class OSMManipulator:
    def __init__(self, node_id_start=0):
        self.current_node_id = node_id_start
        self.gh_docker_controller = DockerGraphhopperController()

    @staticmethod
    def download_map():
        import osmnx as ox
        graph = ox.graph_from_address('Markusplatz, Bamberg, Oberfranken, Bayern, 96047, Deutschland',
                                      network_type='all',
                                      distance=300)
        print("LOADED", graph)
        return graph

    @staticmethod
    def load_map():
        return ox.graph_from_file(f'{OSM_OUTPUT_DIR}/{OSM_OUTPUT_FILENAME}.osm')

    @staticmethod
    def load_geojson():
        with open('/open_spaces/markusplatz.geojson') as f:
            return json.load(f)

    @staticmethod
    def plot_graph(G):
        ox.plot_graph(G, save=True, file_format='svg', filename=f'{OSM_OUTPUT_DIR}/network_plot', edge_linewidth=0.2,
                      node_size=2)

    @staticmethod
    def save_graph(G):
        ox.save_graph_osm(G, filename=f'{OSM_OUTPUT_FILENAME}.osm', folder=OSM_OUTPUT_DIR)

    def get_polygons(self, geojson):
        walkables = []
        restricted = []
        for feature in geojson['features']:
            if "walkable" in feature['properties']:
                if feature['properties']['walkable'] == 'True':
                    walkables.append(feature['geometry']['coordinates'][0])
                else:
                    restricted.append(feature['geometry']['coordinates'][0])
        return walkables, restricted

    def get_entry_points(self, geojson):
        entry_points = []
        for feature in geojson['features']:
            if "entry" in feature['properties'] and feature['properties']['entry'] == "True":
                entry_points.append(feature['geometry']['coordinates'])
        return entry_points

    def get_polygon(self, geojson):
        walkables, restricted = self.get_polygons(geojson)
        return {'walkables': walkables, 'restricted': restricted}

    def add_osm_node(self, G, node_id, coords):
        G.add_node(node_id, osmid=node_id, x=coords[0], y=coords[1])

    def add_osm_edge(self, G, from_node, to_node):
        G.add_edge(from_id, to_id,
                   highway='pedestrian',
                   lanes='1',
                   name='Test',
                   oneway=True,
                   length=10)

    def add_open_space_to_graph(self, G, open_space):
        open_space_nodes = {'walkables': [], 'restricted': []}
        for walkable in open_space['walkables']:
            walkable_nodes = self.add_polygon_to_graph(G, walkable)
            open_space_nodes['walkables'].append(walkable_nodes)
        for restricted in open_space['restricted']:
            restricted_nodes = self.add_polygon_to_graph(G, restricted)
            open_space_nodes['restricted'].append(restricted_nodes)
        return open_space_nodes

    def add_polygon_to_graph(self, G, walkables):
        self.current_node_id += 1
        origin = walkables.pop()
        self.add_osm_node(G, self.current_node_id, origin)
        nodes = [{'node_id': self.current_node_id, 'coord': origin}]
        self.current_node_id += 1
        for coord in walkables:
            self.add_osm_node(G, self.current_node_id, coord)
            self.add_osm_edge(G, nodes[-1]['node_id'], self.current_node_id, nodes[-1]['coord'])
            nodes.append({'node_id': self.current_node_id, 'coord': coord})
            self.current_node_id += 1
        self.add_osm_edge(G, nodes[-1]['node_id'], nodes[0]['node_id'])
        return nodes

    def add_entry_point_edges(self, G, nodes):
        for node in nodes:
            self.add_osm_edge(G, node['node_id'], node['entry_point_id'])

    def add_nodes(self, G, nodes):
        current_node_id = 0
        node_ids = []
        for node in nodes:
            latitude = node[1]
            longitude = node[0]
            G.add_node(current_node_id, osmid=current_node_id, x=longitude, y=latitude)
            node_ids.append(current_node_id)
            current_node_id += 1
        print(G.nodes.data())
        return node_ids

    def create_edges_between_all_nodes(self, G, node_ids):
        for node_id_from in node_ids:
            for node_id_to in node_ids:
                if node_id_from < node_id_to:
                    # TODO: distance calculation
                    G.add_edge(node_id_from, node_id_to, attr_dict={'length': 10, 'highway': 'pedestrian'})

    def create_visibility_graph(self, G, polygon_coordinates):
        node_ids = self.add_nodes(G, polygon_coordinates)
        self.create_edges_between_all_nodes(G, node_ids)

    def test_visablity_graph(self, G):
        coord_dict = self.get_entry_points(G, self.get_polygon_from_geojson())
        nodes = self.add_open_space_to_graph(G, coord_dict)
        self.add_entry_point_edges(G, nodes)

    def get_connection_points(self, entry_points):
        entry_point_street_node_map = []
        for entry_point in entry_points:
            node, dist = ox.get_nearest_node(G, self.get_inverse_coord(entry_point), return_dist=True)
            print(dist)
            entry_point_street_node_map.append({'street_node_id': node, 'entry_coord': entry_point})
        return entry_point_street_node_map

    def add_entry_point_connection(self, G, entry_point_street_node_map):
        for point_obj in entry_point_street_node_map:
            node, dist = ox.get_nearest_node(G, self.get_inverse_coord(point_obj['entry_coord']), return_dist=True)
            print(dist)
            self.add_osm_edge(G, node, point_obj['street_node_id'])

    def get_inverse_coord(self, coord):
        return [coord[1], coord[0]]

    def insert_open_space(self, G):
        geojson = self.load_geojson()
        open_space = self.get_polygon(geojson)
        entry_points = self.get_entry_points(geojson)
        entry_points_map = self.get_connection_points(entry_points)
        open_space_nodes = self.add_open_space_to_graph(G, open_space)
        self.get_visiblity_graph_edges(open_space_nodes)
        self.add_entry_point_connection(G, entry_points_map)

    def test_open_space(self):
        G = OSMManipulator.download_map()
        G = ox.graph_from_address('Markusplatz, Bamberg, Oberfranken, Bayern, 96047, Deutschland', network_type='all',
                                  distance=300)
        print(G)
        self.insert_open_space(G)
        self.gh_docker_controller.clean_graphhopper_restart()

    def get_all_nodes(self, open_space):
        nodes = []
        for elem in open_space['walkables']:
            nodes.extend(elem)
        for elem in open_space['restricted']:
            nodes.extend(elem)
        return nodes

    def get_visiblity_graph_edges(self, open_space):
        added_edges = 0
        open_space_polygon_arr = [[elem['coord'][0], elem['coord'][1]] for elem in open_space['walkables'][0]]
        open_space_poly = Polygon(open_space_polygon_arr)
        prep_open_space_poly = prep(open_space_poly)
        prep_not_walkable_poly = prep(
            Polygon([[elem['coord'][0], elem['coord'][1]] for elem in open_space['restricted'][0]]))
        nodes = self.get_all_nodes(open_space)

        for open_space_elem_from in nodes:
            for open_space_elem_to in nodes:
                if open_space_elem_from['node_id'] < open_space_elem_to['node_id']:
                    new_possible_edge = LineString([open_space_elem_from['coord'], open_space_elem_to['coord']])
                    if prep_open_space_poly.covers(new_possible_edge) and (not prep_not_walkable_poly.intersects(
                            new_possible_edge) or prep_not_walkable_poly.touches(new_possible_edge)):
                        added_edges += 1
                        self.add_osm_edge(G, open_space_elem_from['node_id'], open_space_elem_to['node_id'])

        print(f'ADDED_EDGES:\t{added_edges}')


if __name__ == '__main__':
    G = ox.graph_from_address('Markusplatz, Bamberg, Oberfranken, Bayern, 96047, Deutschland', network_type='all',
                              distance=300)
    # pprint(G.edges.data())
    osmman = OSMManipulator()
    osmman.insert_open_space(G)
    osmman.gh_docker_controller.clean_graphhopper_restart()

    print("GRAPH LOADED")
    osmman.plot_graph(G)
    print("GRAPH PLOTTED")
    osmman.save_graph(G)

    gh_controller = DockerGraphhopperController()
    gh_controller.clean_graphhopper_restart()
