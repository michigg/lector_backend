import logging
from typing import List

import osmnx as ox

from building_controller.controller import GraphBuildingController
from lector.utils.graph_open_space_models import GraphOpenSpace
from lector.utils.open_space_config_controller import OpenSpaceConfigController
from lector.utils.open_space_models import BBox

logger = logging.getLogger(__name__)

ox.config(log_console=False, use_cache=True)

BAMBERG_BBOX = BBox(*[49.925145775384436, 49.865874134216426, 10.951995849609375, 10.836982727050781])

OSM_OUTPUT_FILENAME = "data"
OSM_OUTPUT_DIR = "/osm_data"
SERVICE_NAME = 'graphhopper'

OPEN_SPACE_CONFIG_DIR = "/configs/open_spaces"


class OSMManipulator:
    def __init__(self):
        self.graph = None
        self.current_osm_id = 0
        self.osp_config_c = OpenSpaceConfigController(OPEN_SPACE_CONFIG_DIR)
        self.indoor_map_c = GraphBuildingController(self)

    def create_seperate_open_spaces_plots(self):
        open_spaces = self.osp_config_c.get_open_spaces()
        buildings = self.indoor_map_c.indoor_cc.get_buildings()

        for open_space in open_spaces:
            self.graph = self._download_open_space_network(open_space)
            graph_open_space = self._insert_open_space(buildings, open_space)
            self.plot_graph(output_dir="/osm_data", file_name=graph_open_space.file_name, minimized=False)

    def create_bbox_open_spaces_plot(self):
        open_spaces = self.osp_config_c.get_open_spaces()
        buildings = self.indoor_map_c.indoor_cc.get_buildings()
        self.graph = self.download_map()

        for open_space in open_spaces:
            self._insert_open_space(buildings, open_space)
        self.plot_graph()

    def create_open_space_plot(self, open_space, output_dir="/osm_data"):
        buildings = self.indoor_map_c.indoor_cc.get_buildings()
        self.graph = self.download_map(open_space.get_boundaries(boundary_degree_extension=0.0005))
        graph_open_space = self._insert_open_space(buildings, open_space)
        self.plot_graph(output_dir=output_dir, file_name=graph_open_space.file_name, minimized=False)

    def download_map(self, bbox: BBox = BAMBERG_BBOX):
        return ox.graph_from_bbox(*bbox.get_bbox(), simplify=False)

    @staticmethod
    def load_map():
        return ox.graph_from_file(f'{OSM_OUTPUT_DIR}/{OSM_OUTPUT_FILENAME}.osm')

    def plot_graph(self, output_dir=None, file_name=None, minimized=True):
        if output_dir and file_name and not minimized:
            ox.plot_graph(self.graph,
                          save=True,
                          file_format='svg',
                          filename=f'{output_dir}/{file_name}',
                          edge_linewidth=0.5,
                          node_size=1)
        else:
            ox.plot_graph(self.graph,
                          save=True,
                          file_format='svg',
                          filename=f'{OSM_OUTPUT_DIR}/network_plot',
                          edge_linewidth=0.025,
                          node_size=0.1)

    def save_graph(self):
        ox.save_graph_osm(self.graph,
                          filename=f'{OSM_OUTPUT_FILENAME}.osm',
                          folder=OSM_OUTPUT_DIR,
                          # oneway=False,
                          )
        logger.info(f'Saved osm xml to {OSM_OUTPUT_DIR}/{OSM_OUTPUT_FILENAME}.osm')

    def add_osm_edge(self, from_id, to_id, name, maxspeed=None):
        if maxspeed:
            self.graph.add_edge(from_id, to_id,
                                highway='pedestrian',
                                lanes='1',
                                name=name,
                                oneway=True,
                                maxspeed=maxspeed, )
        else:
            self.graph.add_edge(from_id, to_id,
                                highway='pedestrian',
                                lanes='1',
                                name='Open Space',
                                oneway=True, )

    def add_osm_node(self, coords: List[List[float]]):
        node_id = self._get_new_node_id()
        self.graph.add_node(node_id, osmid=node_id, x=coords[0], y=coords[1])
        return node_id

    def _get_new_node_id(self) -> int:
        self.current_osm_id += 1
        return self.current_osm_id

    def get_nearest_edge(self, coord):
        return ox.get_nearest_edge(self.graph, coord[::-1])

    def get_nearest_point(self, coord):
        return ox.get_nearest_node(self.graph, coord[::-1])

    def get_coord_from_id(self, node_id):
        node = self.graph.node[node_id]
        return [node['x'], node['y']]

    def _download_open_space_network(self, open_space):
        return self.download_map(open_space.get_boundaries(boundary_degree_extension=0.001))

    def _insert_building_to_graph(self, graph_open_space):
        graph_open_space.add_walkable_edges()
        graph_open_space.add_restricted_area_edges()
        graph_buildings = self.indoor_map_c.get_graph_buildings(graph_open_space.buildings)
        self.indoor_map_c.add_buildings_to_graph(graph_buildings)
        graph_open_space.remove_walkable_edges()
        graph_open_space.remove_restricted_area_edges()
        self.plot_graph(output_dir="/osm_data", file_name=f'{graph_open_space.file_name}_building_without_entry',
                        minimized=False)
        for building in graph_buildings:
            for staircase in building.graph_staircases:
                for entry in staircase.get_not_blocked_entries():
                    graph_open_space.add_building_entry_to_open_space(entry)
        self.plot_graph(output_dir="/osm_data", file_name=f'{graph_open_space.file_name}_building', minimized=False)

    def _insert_open_space(self, buildings, open_space):
        open_space.set_buildings(buildings)
        graph_open_space = GraphOpenSpace(open_space, osmm=self)
        # Insert Building Nodes
        self._insert_building_to_graph(graph_open_space)
        # Generate Visibility graph
        graph_open_space.add_visibility_graph_edges()
        graph_open_space.add_graph_entry_points()
        return graph_open_space
