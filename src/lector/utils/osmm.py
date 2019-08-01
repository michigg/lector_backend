import logging

import osmnx as ox
from lector.utils.open_space_config_controller import OpenSpaceConfigController
from lector.utils.open_space_controller import OpenSpace, GraphOpenSpace

logger = logging.getLogger(__name__)

ox.config(log_console=False, use_cache=True)

BAMBERG_BBOX = [49.925145775384436, 49.865874134216426, 10.951995849609375, 10.836982727050781]
# BAMBERG_BBOX = [49.9954, 49.7511, 10.7515, 11.1909]

OSM_OUTPUT_FILENAME = "data"
OSM_OUTPUT_DIR = "/osm_data"
SERVICE_NAME = 'graphhopper'
OPEN_SPACE_CONFIG_DIR = "/open_spaces"


class OSMManipulator:
    def __init__(self):
        self.osp_config_c = OpenSpaceConfigController(OPEN_SPACE_CONFIG_DIR)
        self.graph = self.download_map()
        self.current_node_id = 0
        self.inserted_open_spaces = []

    def insert_open_spaces(self):
        open_spaces = self.osp_config_c.get_open_spaces()
        for open_space in open_spaces:
            self.insert_open_space(open_space)

    def insert_open_space(self, open_space: OpenSpace):
        logger.info(f'Insert Open Space')
        logger.info(f'Graph Nodes: {len(self.graph)}')
        graph_open_space = GraphOpenSpace(open_space, self.graph, self.current_node_id)
        graph_open_space.add_visiblity_graph_edges()
        graph_open_space.add_entry_edges()
        # graph_open_space.add_walkable_edges()
        # graph_open_space.add_restricted_area_edges()
        self.current_node_id = graph_open_space.current_osm_id
        self.inserted_open_spaces.append(graph_open_space)
        logger.info(f'Graph Nodes: {len(self.graph)}')

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
