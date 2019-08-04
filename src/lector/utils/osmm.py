import logging

import osmnx as ox
from shapely.geometry import Point
from shapely.ops import nearest_points

from indoor_mapper.utils.indoor_mapper import IndoorMapController
from lector.utils.open_space_controller import OpenSpaceController
from lector.utils.open_space_models import EntryPoint

logger = logging.getLogger(__name__)

ox.config(log_console=False, use_cache=True)

BAMBERG_BBOX = [49.925145775384436, 49.865874134216426, 10.951995849609375, 10.836982727050781]
# BAMBERG_BBOX = [49.9954, 49.7511, 10.7515, 11.1909]

OSM_OUTPUT_FILENAME = "data"
OSM_OUTPUT_DIR = "/osm_data"
SERVICE_NAME = 'graphhopper'


class OSMManipulator:
    def __init__(self):
        self.graph = self.download_map()
        self.current_osm_id = 0
        self.osp_c = OpenSpaceController(self)
        self.indoor_map_c = IndoorMapController(self)

    def add_open_spaces(self):
        self.osp_c.insert_open_spaces()

    def add_indoor_maps(self):
        self.indoor_map_c.load_indoor_map_data()
        self.indoor_map_c.indoor_maps_to_graph()
        self.indoor_map_c.add_staircase_to_graph()

    @staticmethod
    def download_map():
        return ox.graph_from_address('Markusplatz, Bamberg, Oberfranken, Bayern, 96047, Deutschland',
                                     network_type='all',
                                     distance=1200)
        # return ox.graph_from_address('Markusplatz, Bamberg, Oberfranken, Bayern, 96047, Deutschland',
        #                              network_type='all',
        #                              distance=500)
        # return ox.graph_from_bbox(*BAMBERG_BBOX)

        # return ox.graph_from_bbox(*BAMBERG_BBOX)

    @staticmethod
    def load_map():
        return ox.graph_from_file(f'{OSM_OUTPUT_DIR}/{OSM_OUTPUT_FILENAME}.osm')

    def plot_graph(self):
        ox.plot_graph(self.graph,
                      save=True,
                      file_format='svg',
                      filename=f'{OSM_OUTPUT_DIR}/network_plot',
                      edge_linewidth=0.05,
                      node_size=0.5)

    def save_graph(self):
        ox.save_graph_osm(self.graph, filename=f'{OSM_OUTPUT_FILENAME}.osm',
                          folder=OSM_OUTPUT_DIR)
        logger.info(f'Saved osm xml to {OSM_OUTPUT_DIR}/{OSM_OUTPUT_FILENAME}.osm')

    def add_osm_edge(self, from_id, to_id):
        self.graph.add_edge(from_id, to_id,
                            highway='pedestrian',
                            lanes='1',
                            name='Test',
                            oneway=True,
                            length=40)

    def add_osm_node(self, coords):
        node_id = self._get_new_node_id()
        self.graph.add_node(node_id, osmid=node_id, x=coords[0], y=coords[1])

    def _get_new_node_id(self) -> int:
        self.current_osm_id += 1
        return self.current_osm_id

    def set_nearest_point_to_entry(self, entry_point: EntryPoint) -> (Point, int, int):
        nearest_edge = ox.get_nearest_edge(self.graph, entry_point.open_space_coord[::-1])
        entry_point_shply = Point(*entry_point.open_space_coord)
        nearest_point = nearest_points(entry_point_shply, nearest_edge[0])[1]
        entry_point.graph_entry_node_coord = [nearest_point.x, nearest_point.y]
        entry_point.graph_entry_edge = [nearest_edge[1], nearest_edge[2]]

    def get_coord_from_id(self, node_id):
        node = self.graph.node[node_id]
        return [node['x'], node['y']]

    def add_entry_edges(self, entry_points):
        edges = len(self.graph.edges)
        for entry_point in entry_points:
            self.add_osm_node(entry_point.graph_entry_node_coord)
            entry_point.nearest_graph_node_id = self.current_osm_id
            self.add_osm_edge(entry_point.graph_entry_edge[0], entry_point.nearest_graph_node_id)
            self.add_osm_edge(entry_point.graph_entry_edge[1], entry_point.nearest_graph_node_id)
            self.add_osm_edge(entry_point.nearest_graph_node_id, entry_point.open_space_node_id)
        print(f'ADDED EDGES ENTRY: {len(self.graph.edges) - edges}')
