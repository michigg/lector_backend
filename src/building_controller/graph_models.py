from typing import List

from building_controller.models import StairCase, Building
from lector.utils.open_space_models import GraphBuildingEntryPoint


class GraphStairCase(StairCase):
    def __init__(self, staircase: StairCase, position_id: int, graph_entries: List[GraphBuildingEntryPoint]):
        super().__init__(staircase.name, staircase.floors, staircase.coord, staircase.entries, staircase.blocked,
                         staircase.neighbours)
        self.position_id = position_id
        self.graph_entries = graph_entries

    def get_not_blocked_entries(self):
        if self.is_blocked():
            return []
        return [entry for entry in self.graph_entries if not entry.is_blocked()]


class GraphBuilding(Building):
    def __init__(self, osmm, building: Building, graph_staircases: List[GraphStairCase]):
        super().__init__(building.key, building.staircases)
        self.osmm = osmm
        self.graph_staircases = graph_staircases

    def get_staircaise_neighbours(self, staircase: StairCase):
        if staircase.neighbours:
            return [graph_staircase for graph_staircase in self.graph_staircases if
                    graph_staircase.name in staircase.neighbours]
        return []

    def add_staircase_edges(self):
        for graph_staircase in self.graph_staircases:
            if not graph_staircase.is_blocked():
                for entry in graph_staircase.graph_entries:
                    if not entry.is_blocked():
                        self.osmm.add_osm_edge(graph_staircase.position_id, entry.nearest_graph_node_id, self.key)
                        entry.add_edges()
            for alternate_staircase in self.get_staircaise_neighbours(graph_staircase):
                self.osmm.add_osm_edge(graph_staircase.position_id,
                                       alternate_staircase.position_id,
                                       maxspeed=0.01,
                                       name=self.key)
