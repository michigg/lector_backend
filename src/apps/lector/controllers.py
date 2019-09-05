import logging
from typing import List

import osmnx as ox

from apps.building_controller.config_controller import BuildingConfigController
from apps.building_controller.controller import GraphBuildingController
from apps.building_controller.models import Building
from apps.open_space_controller.config_controller import OpenSpaceConfigController
from apps.open_space_controller.graph_models import GraphOpenSpace
from apps.open_space_controller.models import BBox, OpenSpace

logger = logging.getLogger(__name__)

ox.config(log_console=False, use_cache=True)

BAMBERG_BBOX = BBox(*[49.925145775384436, 49.865874134216426, 10.951995849609375, 10.836982727050781])

OSM_OUTPUT_FILENAME = "data"
OSM_OUTPUT_DIR = "/osm_data"
SERVICE_NAME = 'graphhopper'

OPEN_SPACE_CONFIG_DIR = "/data/open_spaces"
BUILDING_CONFIG_DIR = "/data/indoor_maps"


class OSMController:
    def __init__(self, open_space_config_dir=OPEN_SPACE_CONFIG_DIR, building_config_dir=BUILDING_CONFIG_DIR):
        self.graph = None
        self.current_osm_id = 0
        self.osp_config_c = OpenSpaceConfigController(open_space_config_dir)
        building_cc = BuildingConfigController(config_dir=building_config_dir)
        self.indoor_map_c = GraphBuildingController(self, building_cc=building_cc)

    def create_bbox_open_spaces_plot(self):
        open_spaces = self.osp_config_c.get_open_spaces()
        buildings = self.indoor_map_c.building_cc.get_buildings()
        self.graph = self.download_map()

        for open_space in open_spaces:
            graph_open_space = GraphOpenSpace(open_space, osmm=self)
            self._insert_open_space(buildings, graph_open_space)
        self.plot_graph()

    def create_complete_open_space_plot(self, open_space, output_dir="/osm_data", file_name=None):
        buildings = self.indoor_map_c.building_cc.get_buildings()
        graph_open_space = self._init_open_space_graph(open_space)
        self._insert_open_space(buildings, graph_open_space)
        self.plot_graph(output_dir=output_dir,
                        file_name=file_name if file_name else graph_open_space.file_name,
                        minimized=False)

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
                                name=name,
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

    def get_coord_from_id(self, node_id):
        node = self.graph.node[node_id]
        return [node['x'], node['y']]

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

    def _insert_open_space(self, buildings: List[Building], graph_open_space: GraphOpenSpace):
        self._instert_open_space_buildings(buildings, graph_open_space)
        self._insert_open_space_visibility_graph(graph_open_space)
        self._insert_open_space_entries(graph_open_space)

    def _instert_open_space_buildings(self, buildings: List[Building], graph_open_space: GraphOpenSpace):
        graph_open_space.set_buildings(buildings)
        self._insert_building_to_graph(graph_open_space)

    def _insert_open_space_walkable(self, graph_open_space: GraphOpenSpace):
        graph_open_space.add_walkable_edges()

    def _insert_open_space_restricted(self, graph_open_space: GraphOpenSpace):
        graph_open_space.add_restricted_area_edges()

    def _insert_open_space_visibility_graph(self, graph_open_space: GraphOpenSpace):
        graph_open_space.add_visibility_graph_edges()

    def _insert_open_space_entries(self, graph_open_space: GraphOpenSpace):
        graph_open_space.add_graph_entry_points()

    def create_open_space_walkable_plot(self, open_space, output_dir="/osm_data", file_name=None):
        graph_open_space = self._init_open_space_graph(open_space)
        self._insert_open_space_walkable(graph_open_space)
        self.plot_graph(output_dir=output_dir,
                        file_name=file_name if file_name else graph_open_space.file_name,
                        minimized=False)

    def create_open_space_restricted_plot(self, open_space, output_dir="/osm_data", file_name=None):
        graph_open_space = self._init_open_space_graph(open_space)
        self._insert_open_space_restricted(graph_open_space)
        self.plot_graph(output_dir=output_dir,
                        file_name=file_name if file_name else graph_open_space.file_name,
                        minimized=False)

    def create_open_space_visibility_graph_plot(self, open_space, output_dir="/osm_data", file_name=None):
        graph_open_space = self._init_open_space_graph(open_space)
        self._insert_open_space_visibility_graph(graph_open_space)
        self.plot_graph(output_dir=output_dir,
                        file_name=file_name if file_name else graph_open_space.file_name,
                        minimized=False)

    def create_open_space_entries_plot(self, open_space, output_dir="/osm_data", file_name=None):
        graph_open_space = self._init_open_space_graph(open_space)
        self._insert_open_space_entries(graph_open_space)
        self.plot_graph(output_dir=output_dir,
                        file_name=file_name if file_name else graph_open_space.file_name,
                        minimized=False)

    def create_open_space_walkable_restricted_plot(self, open_space, output_dir="/osm_data", file_name=None):
        graph_open_space = self._init_open_space_graph(open_space)
        self._insert_open_space_walkable(graph_open_space)
        self._insert_open_space_restricted(graph_open_space)
        self.plot_graph(output_dir=output_dir,
                        file_name=file_name if file_name else graph_open_space.file_name,
                        minimized=False)

    def create_open_space_walkable_restricted_entries_plot(self, open_space, output_dir="/osm_data", file_name=None):
        graph_open_space = self._init_open_space_graph(open_space)
        self._insert_open_space_walkable(graph_open_space)
        self._insert_open_space_restricted(graph_open_space)
        self._insert_open_space_entries(graph_open_space)
        self.plot_graph(output_dir=output_dir,
                        file_name=file_name if file_name else graph_open_space.file_name,
                        minimized=False)

    def create_open_space_buildings_plot(self, open_space: OpenSpace, buildings: [], output_dir="/osm_data",
                                         file_name=None):
        graph_open_space = self._init_open_space_graph(open_space)
        self._instert_open_space_buildings(buildings, graph_open_space)
        self._insert_open_space_walkable(graph_open_space)
        self._insert_open_space_restricted(graph_open_space)
        self._insert_open_space_entries(graph_open_space)
        self.plot_graph(output_dir=output_dir,
                        file_name=file_name if file_name else graph_open_space.file_name,
                        minimized=False)

    def _init_open_space_graph(self, open_space):
        self.graph = self.download_map(open_space.get_boundaries(boundary_degree_extension=0.0005))
        graph_open_space = GraphOpenSpace(open_space, osmm=self)
        return graph_open_space
