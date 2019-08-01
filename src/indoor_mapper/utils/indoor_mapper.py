import logging
from typing import List

import osmnx as ox
import requests
import xmltodict
from lector.utils.open_space_controller import EntryPoint
from lector.utils.osmm import OSMManipulator
from networkx import DiGraph
from shapely.geometry import Point
from shapely.ops import nearest_points

from src.indoor_mapper.utils.building_models import GraphStairCase, GraphBuilding
from src.indoor_mapper.utils.config_controller import IndoorMapperConfigController
from src.indoor_mapper.utils.univis_models import Room

logger = logging.getLogger(__name__)


class GraphManipulator:
    def __init__(self, start_node_id: int, graph: DiGraph):
        self.current_osm_id = start_node_id
        self.graph = graph

    def add_osm_edge(self, from_id, to_id):
        self.graph.add_edge(from_id, to_id,
                            highway='pedestrian',
                            lanes='1',
                            name='Test',
                            oneway=True,
                            length=40)

    def add_osm_node(self, coords):
        node_id = self._get_new_node_id()
        self.graph.add_node(node_id, osmid=node_id, x=coords[0], y=coords[1])

    def _get_new_node_id(self) -> int:
        self.current_osm_id += 1
        return self.current_osm_id


class UnivISRoomController:
    def __init__(self):
        self.univis_api_base_url = "http://univis.uni-bamberg.de/prg"

    def _get_univis_api_url(self, building_key):
        return f'{self.univis_api_base_url}?search=rooms&name={building_key}&show=xml'

    def loadPage(self, url: str):
        return xmltodict.parse(requests.get(url).content)

    def get_rooms(self, data: dict, building_key: str) -> List[Room]:
        rooms = []
        for room in data['UnivIS']['Room']:
            if str(f'{building_key}/').lower() in room['short'].lower():
                rooms.append(Room(room))
        return rooms

    def getPersons(self, data: dict):
        persons = []
        for person in data['UnivIS']['Person']:
            persons.append(person)
        return persons

    def get_rooms_by_building_key(self, building_key) -> List[Room]:
        data = self.loadPage(self._get_univis_api_url(building_key))
        return self.get_rooms(data, building_key)


class IndoorMapController(GraphManipulator):
    def __init__(self, osmm: OSMManipulator):
        super().__init__(osmm.current_node_id, osmm.graph)
        self.univis_c = UnivISRoomController()
        self.indoor_cc = IndoorMapperConfigController()
        self.graph_buildings = None
        self.osmm = osmm
        self.graph = osmm.graph

    def load_indoor_map_data(self):
        for building in self.indoor_cc.buildings:
            rooms = self.univis_c.get_rooms_by_building_key(building.key)
            for staircase in building.staircases:
                for floor in staircase.floors:
                    for room in rooms:
                        if room.level == floor.level and floor.room_range_min <= room.number <= floor.room_range_max:
                            staircase.add_room(room)
                            rooms.pop()

    def indoor_maps_to_graph(self) -> List[GraphBuilding]:
        nodes = len(self.graph.nodes)
        graph_buildings = []
        for building in self.indoor_cc.buildings:
            graph_stair_cases = []
            for staircase in building.staircases:
                self.add_osm_node(staircase.coord)
                position_id = self.current_osm_id
                entry_points = []
                for entry in staircase.entries:
                    self.add_osm_node(entry)

                    entry_point = EntryPoint(entry)
                    entry_point.open_space_node_id = self.current_osm_id
                    entry_points.append(entry_point)
                graph_stair_cases.append(GraphStairCase(staircase, position_id, entry_points))
            graph_buildings.append(GraphBuilding(building, graph_stair_cases))
        print(f'ADDED NODES: {len(self.graph.nodes) - nodes}')
        return graph_buildings

    def add_staircase_to_graph(self):
        for building in self.indoor_maps_to_graph():
            for staircase in building.graph_staircases:
                for entry_point in staircase.entry_points:
                    self._set_nearest_point_to_entry(entry_point)
                self.add_entry_edges(staircase.entry_points)
                self.add_staircase_edges(staircase)

    def _set_nearest_point_to_entry(self, entry_point: EntryPoint) -> (Point, int, int):
        nearest_edge = ox.get_nearest_edge(self.graph, entry_point.open_space_coord[::-1])
        entry_point_shply = Point(*entry_point.open_space_coord)
        nearest_point = nearest_points(entry_point_shply, nearest_edge[0])[1]
        entry_point.graph_entry_node_coord = [nearest_point.x, nearest_point.y]
        entry_point.graph_entry_edge = [nearest_edge[1], nearest_edge[2]]

    def add_entry_edges(self, entry_points):
        edges = len(self.graph.edges)
        for entry_point in entry_points:
            self.add_osm_node(entry_point.graph_entry_node_coord)
            entry_point.nearest_graph_node_id = self.current_osm_id
            self.add_osm_edge(entry_point.graph_entry_edge[0], entry_point.nearest_graph_node_id)
            self.add_osm_edge(entry_point.graph_entry_edge[1], entry_point.nearest_graph_node_id)
            self.add_osm_edge(entry_point.nearest_graph_node_id, entry_point.open_space_node_id)
        print(f'ADDED EDGES ENTRY: {len(self.graph.edges) - edges}')

    def add_staircase_edges(self, staircase: GraphStairCase):
        edges = len(self.graph.edges)
        for entry in staircase.entry_points:
            self.add_osm_edge(staircase.position_id, entry.open_space_node_id)
        print(f'ADDED EDGES STAIRCASE: {len(self.graph.edges) - edges}')

    def print_buildings(self):
        for building in self.indoor_cc.buildings:
            print(building)
