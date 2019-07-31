import logging
from typing import List

import osmnx as ox
from networkx import DiGraph
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import nearest_points

from shapely.prepared import prep

logger = logging.getLogger(__name__)


class EntryPoint:
    def __init__(self, entry_point):
        self.open_space_coord = entry_point
        self.open_space_node_id = None
        self.nearest_graph_node_id = None
        self.graph_entry_node_coord = None
        self.graph_entry_edge = []


class OpenSpace:
    def __init__(self, walkable_area: List, restricted_areas: List, entry_points: List[EntryPoint]):
        self.walkable_area = walkable_area
        self.restricted_areas = restricted_areas
        self.entry_points = entry_points


class GraphOpenSpace(OpenSpace):
    def __init__(self, open_space: OpenSpace, graph: DiGraph, osm_start_id: int):
        super().__init__(walkable_area=open_space.walkable_area, restricted_areas=open_space.restricted_areas,
                         entry_points=open_space.entry_points)
        self.graph = graph
        self.current_osm_id = osm_start_id
        self.walkable_area_poly = Polygon(open_space.walkable_area)
        self.walkable_area_prep_poly = prep(self.walkable_area_poly)
        self.walkable_area_nodes = []

        self.restricted_area_polys = [Polygon(restricted_area) for restricted_area in self.restricted_areas]
        self.restricted_areas_nodes = []
        self.edges = []
        self._set_node_ids()

    def add_osm_node(self, coords):
        node_id = self.get_new_node_id()
        self.graph.add_node(node_id, osmid=node_id, x=coords[0], y=coords[1])

    def add_osm_edge(self, from_id, to_id):
        self.graph.add_edge(from_id, to_id,
                            highway='pedestrian',
                            lanes='1',
                            name='Test',
                            oneway=True,
                            length=40)

    def _set_nearest_point_to_entry(self, entry_point: EntryPoint) -> (Point, int, int):
        nearest_edge = ox.get_nearest_edge(self.graph, entry_point.open_space_coord[::-1])
        entry_point_shply = Point(*entry_point.open_space_coord)
        nearest_point = nearest_points(entry_point_shply, nearest_edge[0])[1]
        entry_point.graph_entry_node_coord = [nearest_point.x, nearest_point.y]
        entry_point.graph_entry_edge = [nearest_edge[1], nearest_edge[2]]

    def _set_node_ids(self):
        for entry_point in self.entry_points:
            self._set_nearest_point_to_entry(entry_point)

        for point in self.walkable_area:
            self.add_osm_node(point)
            self.walkable_area_nodes.append(self.current_osm_id)

        for entry_point in self.entry_points:
            entry_point.open_space_node_id = ox.get_nearest_node(self.graph, entry_point.open_space_coord[::-1])

        for restricted_area in self.restricted_areas:
            nodes = []
            for point in restricted_area:
                self.add_osm_node(point)
                nodes.append(self.current_osm_id)
            self.restricted_areas_nodes.append(nodes)

    def get_other_restricted_area_polys(self, restricted_area_poly: Polygon) -> List[Polygon]:
        other_restricted_area_polys = self.restricted_area_polys.copy()
        other_restricted_area_polys.remove(restricted_area_poly)
        return other_restricted_area_polys

    def add_edge(self, from_id: int, to_id: int):
        self.edges.append([from_id, to_id])
        self.add_osm_edge(from_id, to_id)

    def is_visible_edge(self, line):
        visible_bools = []
        not_intersect_bools = []
        for restriced_area_poly in self.restricted_area_polys:
            prep_restriced_area_poly = prep(restriced_area_poly)

            expr_not_intersect = not prep_restriced_area_poly.intersects(line)
            expr_touches = prep_restriced_area_poly.touches(line)

            # expr = (expr_not_intersect or expr_touches) and self.line_intersects_no_other_restricted_area(
            #     line, restriced_area_poly)
            visible_bools.append(expr_touches and self.line_intersects_no_other_restricted_area(
                line, restriced_area_poly))
            not_intersect_bools.append(expr_not_intersect)
        return any(visible_bools) or all(not_intersect_bools)

    def is_internal_edge(self, line: LineString) -> bool:
        return self.walkable_area_prep_poly.covers(line)

    def line_intersects_no_other_restricted_area(self, line: LineString, restricted_area_poly: Polygon) -> bool:
        other_restricted_areas = self.get_other_restricted_area_polys(restricted_area_poly)
        if other_restricted_areas:
            return all([not prep(restricted_area).intersects(line) for restricted_area in other_restricted_areas])
        return True

    def get_new_node_id(self) -> int:
        self.current_osm_id += 1
        return self.current_osm_id

    def add_visiblity_graph_edges(self):
        curr_edges = len(self.edges)
        nodes = []
        nodes.extend(self.walkable_area_nodes)
        for restricted_area_nodes in self.restricted_areas_nodes:
            nodes.extend(restricted_area_nodes)
        for node_from in nodes:
            for node_to in nodes:
                if node_from < node_to:
                    new_possible_edge = LineString(
                        [self._get_coord_from_id(node_from), self._get_coord_from_id(node_to)])
                    if self.is_internal_edge(new_possible_edge) and self.is_visible_edge(new_possible_edge):
                        self.add_edge(node_from, node_to)

        logger.info(f'ADDED_EDGES:\t{len(self.edges) - curr_edges}')

    def add_entry_edges(self):
        for entry_point in self.entry_points:
            self.add_osm_node(entry_point.graph_entry_node_coord)
            entry_point.nearest_graph_node_id = self.current_osm_id
            self.add_osm_edge(entry_point.graph_entry_edge[0], entry_point.nearest_graph_node_id)
            self.add_osm_edge(entry_point.graph_entry_edge[1], entry_point.nearest_graph_node_id)
            self.add_osm_edge(entry_point.nearest_graph_node_id, entry_point.open_space_node_id)

    def add_walkable_edges(self):
        self._set_polygon_edges(self.walkable_area_nodes)

    def add_restricted_area_edges(self):
        for restricted_area_nodes in self.restricted_areas_nodes:
            self._set_polygon_edges(restricted_area_nodes)

    def _set_polygon_edges(self, nodes):
        last_node = None
        for node in nodes:
            if last_node:
                self.add_osm_edge(last_node, node)
            last_node = node
        self.add_osm_edge(self.walkable_area_nodes[0], self.walkable_area_nodes[-1])

    def _get_coord_from_id(self, node_id):
        return [self.graph.node[node_id]['x'], self.graph.node[node_id]['y']]
