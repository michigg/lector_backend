from typing import List

from apps.building_controller.models import StairCase, Building, BuildingEntryPoint
from apps.lector.graph_models import GraphEntryPoint


class GraphBuildingEntryPoint(BuildingEntryPoint, GraphEntryPoint):
    def __init__(self, entry_point: BuildingEntryPoint, osmm):
        self.wheelchair = entry_point.wheelchair
        self.blocked = entry_point.blocked
        GraphEntryPoint.__init__(self, entry_point=entry_point, osmm=osmm)


class GraphStairCase(StairCase):
    def __init__(self, staircase: StairCase, position_id: int, graph_entries: List[GraphBuildingEntryPoint]):
        super().__init__(staircase.id,
                         staircase.name,
                         staircase.floors,
                         staircase.coord,
                         staircase.entries,
                         staircase.blocked,
                         staircase.neighbours)
        self.position_id = position_id
        self.graph_entries = graph_entries

    def get_not_blocked_entries(self):
        return [] if self.is_blocked() else [entry for entry in self.graph_entries if not entry.is_blocked()]


class GraphBuilding(Building):
    def __init__(self, osmm, building: Building, graph_staircases: List[GraphStairCase]):
        super().__init__(building.key, building.staircases)
        self.osmm = osmm
        self.graph_staircases = graph_staircases

    def get_staircaise_neighbours(self, staircase: StairCase) -> List[GraphStairCase]:
        if not staircase.neighbours:
            return [graph_staircase for graph_staircase in self.graph_staircases if
                    graph_staircase.id in staircase.neighbours]
        return []

    def add_staircase_edges(self):
        """
        Insert staircase edges into the main graph
        :return:
        """
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
