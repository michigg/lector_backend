from typing import List

import osmnx as ox
from shapely.geometry import Polygon, LineString
from shapely.prepared import prep

from lector.utils.open_space_models import OpenSpace, logger


# from lector.utils.osmm import OSMManipulator


class GraphOpenSpace(OpenSpace):
    def __init__(self, open_space: OpenSpace, osmm):
        super().__init__(file_name=open_space.file_name, walkable_area=open_space.walkable_area,
                         restricted_areas=open_space.restricted_areas,
                         entry_points=open_space.entry_points)
        self.osmm = osmm
        self.walkable_area_poly = Polygon(open_space.walkable_area)
        self.walkable_area_prep_poly = prep(self.walkable_area_poly)
        self.walkable_area_nodes = []

        self.restricted_area_polys = [Polygon(restricted_area) for restricted_area in self.restricted_areas]
        self.restricted_areas_nodes = []
        self.edges = []
        self._set_node_ids()

    def is_open_space_walkable_node(self, node_id):
        return node_id in self.walkable_area_nodes

    def is_open_space_restricted_area_node(self, node_id):
        for index, restricted_area_nodes in enumerate(self.restricted_areas_nodes):
            if node_id in restricted_area_nodes:
                return index
        return -1

    def _set_node_ids(self):
        for entry_point in self.entry_points:
            self.osmm.set_nearest_point_to_entry(entry_point)

        for point in self.walkable_area:
            self.osmm.add_osm_node(point)
            self.walkable_area_nodes.append(self.osmm.current_osm_id)

        for entry_point in self.entry_points:
            entry_point.open_space_node_id = ox.get_nearest_node(self.osmm.graph, entry_point.open_space_coord[::-1])

        for restricted_area in self.restricted_areas:
            nodes = []
            for point in restricted_area:
                self.osmm.add_osm_node(point)
                nodes.append(self.osmm.current_osm_id)
            self.restricted_areas_nodes.append(nodes)

    def get_other_restricted_area_polys(self, restricted_area_poly: Polygon) -> List[Polygon]:
        other_restricted_area_polys = self.restricted_area_polys.copy()
        other_restricted_area_polys.remove(restricted_area_poly)
        return other_restricted_area_polys

    def add_edge(self, from_id: int, to_id: int):
        self.edges.append([from_id, to_id])
        self.osmm.add_osm_edge(from_id, to_id)

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
                        [self.osmm.get_coord_from_id(node_from), self.osmm.get_coord_from_id(node_to)])
                    if self.is_internal_edge(new_possible_edge) and self.is_visible_edge(new_possible_edge):
                        self.add_edge(node_from, node_to)

        logger.info(f'ADDED_EDGES:\t{len(self.edges) - curr_edges}')

    def add_walkable_edges(self):
        self._set_polygon_edges(self.walkable_area_nodes)

    def add_restricted_area_edges(self):
        for restricted_area_nodes in self.restricted_areas_nodes:
            self._set_polygon_edges(restricted_area_nodes)

    def _set_polygon_edges(self, nodes):
        last_node = None
        for node in nodes:
            if last_node:
                self.osmm.add_osm_edge(last_node, node)
            last_node = node
        self.osmm.add_osm_edge(self.walkable_area_nodes[0], self.walkable_area_nodes[-1])
