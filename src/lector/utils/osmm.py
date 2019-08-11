import logging
from typing import List

import osmnx as ox
from shapely.geometry import Point
from shapely.ops import nearest_points

from indoor_mapper.utils.indoor_mapper import IndoorMapController
from lector.utils.graph_open_space_models import GraphOpenSpace
from lector.utils.open_space_controller import OpenSpaceController
from lector.utils.open_space_models import EntryPoint, BuildingEntryPoint

logger = logging.getLogger(__name__)

ox.config(log_console=True, use_cache=True)

BAMBERG_BBOX = [49.925145775384436, 49.865874134216426, 10.951995849609375, 10.836982727050781]

OSM_OUTPUT_FILENAME = "data"
OSM_OUTPUT_DIR = "/osm_data"
SERVICE_NAME = 'graphhopper'


class OSMManipulator:
    def __init__(self):
        self.graph = None
        self.current_osm_id = 0
        self.osp_c = OpenSpaceController(self)
        self.indoor_map_c = IndoorMapController(self)

    def add_open_spaces_with_staircases(self):
        self.download_map()
        graph_open_spaces = self.osp_c.get_graph_open_spaces()
        for graph_open_space in graph_open_spaces:
            self.add_open_space_with_staircases(graph_open_space, graph_open_spaces)

    def add_open_space_with_staircases(self, graph_open_space, graph_open_spaces):
        graph_open_space.add_walkable_edges()
        graph_open_space.add_restricted_area_edges()
        graph_buildings = self.indoor_map_c.add_staircase_to_graph()
        for graph_building in graph_buildings:
            for staircase in graph_building.staircases:
                for entry_point in staircase.entries:
                    self.update_open_spaces(entry_point, graph_open_spaces)
        graph_open_space.add_visiblity_graph_edges()
        self.add_entry_edges(graph_open_space.entry_points)

    #     TODO: Restructure that !!
    def add_custom_open_spaces_with_buildings(self, graph_open_space, graph_open_spaces):
        graph_open_space.add_walkable_edges()
        graph_open_space.add_restricted_area_edges()
        buildings = self.indoor_map_c.get_buildings_for_open_space(graph_open_space)
        graph_buildings = self.indoor_map_c.get_graph_buildings(buildings)
        self.indoor_map_c.add_buildings_to_graph(graph_buildings)
        for graph_building in graph_buildings:
            for staircase in graph_building.staircases:
                for entry_point in staircase.entries:
                    self.update_open_spaces(entry_point, graph_open_spaces)
        graph_open_space.add_visiblity_graph_edges()
        self.add_entry_edges(graph_open_space.entry_points)


    def update_open_spaces(self, entry_point: BuildingEntryPoint, graph_open_spaces: List[GraphOpenSpace]):
        for graph_open_space in graph_open_spaces:
            print("Open Space", graph_open_space)
            if graph_open_space.is_open_space_walkable_node(entry_point.graph_entry_edge[0]):
                graph_open_space.walkable_area_nodes.append(entry_point.open_space_node_id)
                graph_open_space.walkable_area_nodes = sorted(graph_open_space.walkable_area_nodes)
                print("Graph Walkable: ", graph_open_space.walkable_area_nodes)
            restricted_area_id = graph_open_space.is_open_space_restricted_area_node(entry_point.graph_entry_edge[0])
            if graph_open_space.is_open_space_restricted_area_node(entry_point.graph_entry_edge[0]) > -1:
                graph_open_space.restricted_areas_nodes[restricted_area_id].append(entry_point.open_space_node_id)
                graph_open_space.restricted_areas_nodes[restricted_area_id] = sorted(
                    graph_open_space.restricted_areas_nodes[restricted_area_id])
                print(f"Graph Restricted: {restricted_area_id}",
                      graph_open_space.restricted_areas_nodes[restricted_area_id])

    def add_open_spaces(self):
        self.osp_c.insert_open_spaces()

    def add_indoor_maps(self):
        # self.indoor_map_c.load_indoor_map_data()
        self.indoor_map_c.indoor_maps_to_graph()
        self.indoor_map_c.add_staircase_to_graph()

    def download_map(self, bbox: List[float] = BAMBERG_BBOX):
        self.graph = ox.graph_from_bbox(*bbox, simplify=False)
        return self.graph

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
                          node_tags=['highway'],
                          node_attrs=['id', 'timestamp', 'uid', 'user', 'version', 'changeset', 'lat', 'lon'],
                          edge_tags=['highway', 'lanes', 'maxspeed', 'name', 'oneway'],
                          edge_attrs=['id', 'timestamp', 'uid', 'user', 'version', 'changeset'])
        logger.info(f'Saved osm xml to {OSM_OUTPUT_DIR}/{OSM_OUTPUT_FILENAME}.osm')

    def add_osm_edge(self, from_id, to_id):
        self.graph.add_edge(from_id, to_id,
                            highway='pedestrian',
                            lanes='1',
                            name='Open Space',
                            oneway=True,
                            )

    def add_osm_node(self, coords: List[List[float]]):
        node_id = self._get_new_node_id()
        self.graph.add_node(node_id, osmid=node_id, x=coords[0], y=coords[1])
        return node_id

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
            entry_point.nearest_graph_node_id = self.add_osm_node(entry_point.graph_entry_node_coord)
            self.add_osm_edge(entry_point.graph_entry_edge[0], entry_point.nearest_graph_node_id)
            self.add_osm_edge(entry_point.graph_entry_edge[1], entry_point.nearest_graph_node_id)
            self.add_osm_edge(entry_point.nearest_graph_node_id, entry_point.open_space_node_id)
        print(f'ADDED EDGES ENTRY: {len(self.graph.edges) - edges}')
