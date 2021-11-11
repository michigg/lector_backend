import logging
from collections import namedtuple
from enum import Enum
from typing import List

import osmnx as ox
from shapely.geometry import LineString

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

OPEN_SPACE_CONFIG_DIR = "/configs/open_spaces"
BUILDING_CONFIG_DIR = "/configs/indoor_maps"


class EDGE_TYPES(Enum):
    NORMAL = 0
    OPEN_SPACE_ENTRY = 1
    OPEN_SPACE_VISIBLITY = 2
    OPEN_SPACE_WALKABLE = 3
    OPEN_SPACE_RESTRICTED = 4
    BUILDING_ENTRY = 5
    BUILDING_STAIRCASE = 6


COLOR_MAP = {EDGE_TYPES.NORMAL: "#000000",
             EDGE_TYPES.OPEN_SPACE_ENTRY: "#0f0f0f",
             EDGE_TYPES.OPEN_SPACE_VISIBLITY: "#9ccc3c",
             EDGE_TYPES.OPEN_SPACE_RESTRICTED: "#e70066",
             EDGE_TYPES.OPEN_SPACE_WALKABLE: "#14278d",
             EDGE_TYPES.BUILDING_ENTRY: "#5d2612",
             EDGE_TYPES.BUILDING_STAIRCASE: "#9ccc3c"
             }


class OSMController:
    def __init__(self, open_space_config_dir=OPEN_SPACE_CONFIG_DIR, building_config_dir=BUILDING_CONFIG_DIR):
        self.graph = None
        self.current_osm_id = 0
        self.osp_config_c = OpenSpaceConfigController(open_space_config_dir)
        building_cc = BuildingConfigController(config_dir=building_config_dir)
        self.indoor_map_c = GraphBuildingController(self, building_cc=building_cc)

    def create_bbox_open_spaces_plot(self, bbox=None):
        open_spaces = self.osp_config_c.get_open_spaces()
        buildings = self.indoor_map_c.building_cc.get_buildings()
        self.graph = self.download_map(bbox) if bbox else self.download_map()

        for open_space in open_spaces:
            if self._is_contained_open_space(open_space, bbox):
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
                          filepath=f'{output_dir}/{file_name}.svg',
                          edge_linewidth=0.5,
                          node_size=1)
        else:
            ox.plot_graph(self.graph,
                          save=True,
                          filepath=f'{OSM_OUTPUT_DIR}/network_plot.svg',
                          edge_linewidth=0.025,
                          node_size=0.1)

    def save_graph(self):
        ox.save_graph_xml(self.graph,
                          filepath=f'{OSM_OUTPUT_DIR}/{OSM_OUTPUT_FILENAME}.osm'
                          # oneway=False,
                          )
        logger.info(f'Saved osm xml to {OSM_OUTPUT_DIR}/{OSM_OUTPUT_FILENAME}.osm')

    def add_osm_edge(self, from_id, to_id, name, maxspeed=None, type=EDGE_TYPES.NORMAL):
        if maxspeed:
            self.graph.add_edge(from_id, to_id,
                                highway='pedestrian',
                                lanes='1',
                                name=name,
                                oneway=True,
                                maxspeed=maxspeed,
                                color_label=type)
        else:
            self.graph.add_edge(from_id, to_id,
                                highway='pedestrian',
                                lanes='1',
                                name=name,
                                oneway=True,
                                color_label=type)

    def add_osm_node(self, coords: List[List[float]]):
        node_id = self._get_new_node_id()
        self.graph.add_node(node_id, osmid=node_id, x=coords[0], y=coords[1])
        return node_id

    def _get_new_node_id(self) -> int:
        self.current_osm_id += 1
        return self.current_osm_id

    def get_nearest_edge(self, coord) -> (int, int, int, LineString):
        x = coord[0]
        y = coord[1]
        # Returns nearest edge with (startNodeId, stopNodeId, edgeId)
        nearest_edge = ox.nearest_edges(self.graph, x, y)
        start_node_coord = self.get_coord_from_id(nearest_edge[0])
        stop_node_coord = self.get_coord_from_id(nearest_edge[1])
        print("get_nearest_edge", coord, start_node_coord, stop_node_coord)
        result = namedtuple("NearestEdge", ["start_node_id", "stop_node_id", "edge_id", "geom"])
        return result(*nearest_edge, LineString(coordinates=[start_node_coord, stop_node_coord]))

    def get_coord_from_id(self, node_id):
        node = self.graph.nodes()[node_id]
        return [node['x'], node['y']]

    def _insert_building_to_graph(self, graph_open_space):
        graph_open_space.add_walkable_edges()
        graph_open_space.add_restricted_area_edges()

        graph_buildings = self.indoor_map_c.get_graph_buildings(graph_open_space.buildings)
        logger.info(f'_insert_building_to_graph: Graph Buildings: {graph_buildings}')
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
        self._insert_open_space_buildings(buildings, graph_open_space)
        self._insert_open_space_visibility_graph(graph_open_space)
        self._insert_open_space_entries(graph_open_space)

    def _insert_open_space_buildings(self, buildings: List[Building], graph_open_space: GraphOpenSpace):
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
        self._insert_open_space_buildings(buildings, graph_open_space)
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

    def _is_contained_open_space(self, open_space: OpenSpace, bbox: BBox):
        open_space_bbox = open_space.get_boundaries()
        return bbox.min_lat < open_space_bbox.min_lat \
               and bbox.min_lon < open_space_bbox.min_lon \
               and bbox.max_lat > open_space_bbox.max_lat \
               and bbox.max_lon > open_space_bbox.max_lon
