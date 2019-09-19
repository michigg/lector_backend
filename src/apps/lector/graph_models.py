from shapely.geometry import Point, LineString
from shapely.ops import nearest_points

from .models import EntryPoint


class GraphEntryPoint(EntryPoint):
    """Basic Entry Point Class which include graph functions"""

    def __init__(self, entry_point: EntryPoint, osmm):
        super().__init__(coord=entry_point.open_space_coord)
        self.osmm = osmm
        self.open_space_point = Point(*self.open_space_coord)
        self.graph_entry_node_coord = None
        self.graph_entry_edge = None

        self._set_nearest_graph_entry_node_and_edge()
        self.nearest_graph_node_id = self.osmm.add_osm_node(self.graph_entry_node_coord)

    def _set_nearest_graph_entry_node_and_edge(self):
        """Set the nearest graph node for the graph connection"""
        nearest_edge = self.osmm.get_nearest_edge(self.open_space_coord)
        nearest_point = nearest_points(self.open_space_point, nearest_edge[0])[1]
        self.graph_entry_node_coord = [nearest_point.x, nearest_point.y]
        self.graph_entry_edge = [nearest_edge[1], nearest_edge[2]]

    def get_edge(self) -> LineString:
        return LineString([self.open_space_point, Point(*self.graph_entry_node_coord)])

    def add_edges(self):
        self.osmm.add_osm_edge(self.graph_entry_edge[0], self.nearest_graph_node_id, "Eingang")
        self.osmm.add_osm_edge(self.graph_entry_edge[1], self.nearest_graph_node_id, "Eingang")
