import math
import os
from typing import List

from shapely.geometry import Polygon, LineString, Point
from shapely.prepared import prep

from apps.lector.graph_models import GraphEntryPoint
from apps.lector.models import EntryPoint
from apps.open_space_controller.models import OpenSpace


class OpenSpaceEntryPoint(EntryPoint):
    def __init__(self, coord: List[List[float]]):
        super().__init__(coord)


class GraphOpenSpaceEntryPoint(OpenSpaceEntryPoint, GraphEntryPoint):
    def __init__(self, entry_point: OpenSpaceEntryPoint, osmm, open_space):
        self.open_space_coord = entry_point.open_space_coord
        GraphEntryPoint.__init__(self, entry_point=entry_point, osmm=osmm)
        self.open_space_node = self._set_open_space_entry_point(open_space)

    def _set_open_space_entry_point(self, open_space):
        node_distance_list = []
        for node in open_space.get_all_nodes():
            coord = self.osmm.get_coord_from_id(node)
            distance = math.sqrt(
                math.pow(self.open_space_coord[0] - coord[0], 2) + math.pow(self.open_space_coord[1] - coord[1], 2))
            node_distance_list.append({"distance": distance, "node": node})
        return min(node_distance_list, key=lambda elem: elem['distance'])['node']

    def add_edges(self):
        self.osmm.add_osm_edge(self.graph_entry_edge[0], self.nearest_graph_node_id, "Zugang Freifläche")
        self.osmm.add_osm_edge(self.graph_entry_edge[1], self.nearest_graph_node_id, "Zugang Freifläche")
        self.osmm.add_osm_edge(self.open_space_node, self.nearest_graph_node_id,
                               "Zugang Freifläche")


class GraphOpenSpace(OpenSpace):
    def __init__(self, open_space: OpenSpace, osmm):
        super().__init__(file_name=open_space.file_name,
                         walkable_area=open_space.walkable_area_coords,
                         restricted_areas=open_space.restricted_areas_coords,
                         blocked_areas=open_space.blocked_areas_coords,
                         entry_points=open_space.entry_points,
                         buildings=open_space.buildings)
        self.osmm = osmm
        self.walkable_area_poly = Polygon(open_space.walkable_area_coords)
        self.walkable_area_prep_poly = prep(self.walkable_area_poly)
        self.walkable_area_nodes = []

        self.restricted_area_polys = [Polygon(restricted_area) for restricted_area in self.restricted_areas_coords]
        self.restricted_areas_nodes = []

        self.blocked_area_polys = [Polygon(blocked_area) for blocked_area in self.blocked_areas_coords]
        self.blocked_areas_nodes = []

        self.graph_entry_points = []

        self.edges = []
        #  Remove other nodes
        self.remove_open_space_nodes()
        self._set_node_ids()

    def is_open_space_walkable_node(self, node_id) -> bool:
        return node_id in self.walkable_area_nodes

    def get_open_space_restricted_area_id(self, node_id) -> int:
        for index, restricted_area_nodes in enumerate(self.restricted_areas_nodes):
            if node_id in restricted_area_nodes:
                return index
        return -1

    def get_other_restricted_area_polys(self, restricted_area_poly: Polygon) -> List[Polygon]:
        other_restricted_area_polys = self.restricted_area_polys.copy()
        other_restricted_area_polys.remove(restricted_area_poly)
        return other_restricted_area_polys

    def add_edge(self, from_id: int, to_id: int):
        self.edges.append([from_id, to_id])
        self.osmm.add_osm_edge(from_id, to_id, self.get_name())

    def is_visible_edge(self, line) -> bool:
        if self.is_internal_edge(line):
            is_blocked = any(
                [prep(blocked_area_poly).intersects(line) for blocked_area_poly in self.blocked_area_polys])
            if is_blocked:
                return False

            for restriced_area_poly in self.restricted_area_polys:
                prep_restriced_area_poly = prep(restriced_area_poly)

                if prep_restriced_area_poly.touches(line) and not self.line_intersects_other_restricted_areas(line,
                                                                                                              restriced_area_poly, ):
                    return True
                # Checked: is_blocked_line, is_restricted_line
            is_restricted = self.is_restricted_line(line, self.restricted_area_polys)
            if is_restricted:
                return False
            return True
        return False

    # Better naming Line that overlaps or contains line
    def is_restricted_line(self, line: LineString, restricted_area_polys: List[Polygon]) -> bool:
        return any([prep(restriced_area_poly).intersects(line) for
                    restriced_area_poly in restricted_area_polys])

    def is_internal_edge(self, line: LineString) -> bool:
        return self.walkable_area_prep_poly.covers(line)

    def line_intersects_other_restricted_areas(self, line: LineString, restricted_area_poly: Polygon) -> bool:
        other_restricted_areas = self.get_other_restricted_area_polys(restricted_area_poly)
        for other_restricted_area in other_restricted_areas:
            other_areas = self.get_other_restricted_area_polys(other_restricted_area)
            other_areas.remove(restricted_area_poly)
            if prep(other_restricted_area).touches(line) and not self.is_restricted_line(line, other_areas):
                return False
        return self.is_restricted_line(line, other_restricted_areas)

    def add_visibility_graph_edges(self):
        nodes = self.get_all_nodes()
        for node_from in nodes:
            for node_to in nodes:
                if node_from < node_to:
                    new_possible_edge = LineString(
                        [self.osmm.get_coord_from_id(node_from), self.osmm.get_coord_from_id(node_to)])
                    if self.is_visible_edge(new_possible_edge):
                        self.add_edge(node_from, node_to)

    def add_walkable_edges(self):
        self._set_polygon_edges(self.walkable_area_nodes)

    def remove_walkable_edges(self):
        self._remove_polygon_edges(self.walkable_area_nodes)

    def add_restricted_area_edges(self):
        for restricted_area_nodes in self.restricted_areas_nodes:
            self._set_polygon_edges(restricted_area_nodes)

    def remove_restricted_area_edges(self):
        for restricted_area_nodes in self.restricted_areas_nodes:
            self._remove_polygon_edges(restricted_area_nodes)

    def add_blocked_area_edges(self):
        for blocked_area_nodes in self.blocked_areas_nodes:
            self._set_polygon_edges(blocked_area_nodes)

    def remove_blocked_area_edges(self):
        for blocked_area_nodes in self.blocked_areas_nodes:
            self._remove_polygon_edges(blocked_area_nodes)

    def add_building_entry_to_open_space(self, entry_point):
        if self.is_open_space_walkable_node(entry_point.graph_entry_edge[0]):
            self.insert_sorted(entry_point.nearest_graph_node_id, entry_point.graph_entry_edge[0],
                               self.walkable_area_nodes)
            self.walkable_area_poly = Polygon(
                [[self.osmm.graph.node[node]['x'], self.osmm.graph.node[node]['y']] for node in
                 self.walkable_area_nodes])
            self.walkable_area_prep_poly = prep(self.walkable_area_poly)
        restricted_area_id = self.get_open_space_restricted_area_id(entry_point.graph_entry_edge[0])
        if self.get_open_space_restricted_area_id(entry_point.graph_entry_edge[0]) > -1:
            self.insert_sorted(entry_point.nearest_graph_node_id, entry_point.graph_entry_edge[0],
                               self.restricted_areas_nodes[restricted_area_id])
            self.restricted_area_polys[restricted_area_id] = Polygon(
                [[self.osmm.graph.node[node]['x'], self.osmm.graph.node[node]['y']] for node in
                 self.restricted_areas_nodes[restricted_area_id]])

    def insert_sorted(self, to_insert_node, node_before, nodes):
        for index, node_id in enumerate(nodes):
            if node_id == node_before:
                nodes.insert(index + 1, to_insert_node)
                return

    def _set_node_ids(self):

        # Set Walkable Area Nodes
        self.walkable_area_nodes = [self.osmm.add_osm_node(point) for point in self.walkable_area_coords]

        self.graph_entry_points = [GraphOpenSpaceEntryPoint(entry_point, self.osmm, self) for entry_point in
                                   self.entry_points]
        # self.get_entry_points()

        # Set Restricted Area Nodes
        for restricted_area_coords in self.restricted_areas_coords:
            self.restricted_areas_nodes.append([self.osmm.add_osm_node(coord) for coord in restricted_area_coords])

        # Set Blocked Areas
        for blocked_area_coords in self.blocked_areas_nodes:
            self.blocked_areas_nodes.append([self.osmm.add_osm_node(coord) for coord in blocked_area_coords])

    def get_name(self):
        os.path.basename(self.file_name)

    def _set_polygon_edges(self, nodes):
        last_node = None
        for node in nodes:
            if last_node:
                self.osmm.add_osm_edge(last_node, node, name=self.get_name())
            last_node = node
        self.osmm.add_osm_edge(nodes[0], nodes[-1], name=self.get_name())

    def _remove_polygon_edges(self, nodes):
        last_node = None
        for node in nodes:
            if last_node:
                self.osmm.graph.remove_edge(last_node, node)
            last_node = node
        self.osmm.graph.remove_edge(nodes[0], nodes[-1])

    # Better naming all nodes without blocked space
    def get_all_nodes(self) -> List[int]:
        nodes = []
        nodes.extend(self.walkable_area_nodes)
        for restricted_area_nodes in self.restricted_areas_nodes:
            nodes.extend(restricted_area_nodes)
        return nodes

    def remove_open_space_nodes(self):
        # TODO better
        # bbox = self.get_boundaries(boundary_degree_extension=-0.00035)
        nodes = [node for node, data in self.osmm.graph.nodes(data=True) if
                 self.walkable_area_prep_poly.contains(Point(self.osmm.get_coord_from_id(node)))]
        for node in nodes:
            self.osmm.graph.remove_node(node)

    def add_graph_entry_points(self):
        for graph_entry_point in self.graph_entry_points:
            graph_entry_point.add_edges()

    def plot_areas(self):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        # Plot y vs x as well as z vs x. label will be used by ax.legend() method to generate a legend automatically
        ax.plot(*self.walkable_area_poly.exterior.xy, label='poly')
        for restricted_poly in self.restricted_area_polys:
            ax.plot(*restricted_poly.exterior.xy, label='restricted')
        ax.set_title('Polys')
        handles, labels = ax.get_legend_handles_labels()
        lgd = ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.1))
        text = ax.text(-0.2, 1.05, "Aribitrary text", transform=ax.transAxes)
        ax.grid('on')
        fig.savefig(f'/osm_data/{self.file_name}_polys.svg', bbox_extra_artists=(lgd, text), bbox_inches='tight')
