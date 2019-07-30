import osmnx as ox
from shapely.geometry import Polygon, LineString
from shapely.prepared import prep
from pprint import pprint


class OpenSpaceController:
    def __init__(self, G, node_id_start=0):
        self.graph = G
        self.current_node_id = node_id_start

    def add_osm_node(self, node_id, coords):
        self.graph.add_node(node_id, osmid=node_id, x=coords[0], y=coords[1])

    def add_osm_edge(self, from_id, to_id):
        self.graph.add_edge(from_id, to_id,
                            highway='pedestrian',
                            lanes='1',
                            name='Test',
                            oneway=True,
                            length=10)

    def add_open_space_to_graph(self, open_space):
        open_space_nodes = {'walkables': [], 'restricted': []}
        for walkable in open_space['walkables']:
            walkable_nodes = self.add_polygon_to_graph(walkable)
            open_space_nodes['walkables'].append(walkable_nodes)
        for restricted in open_space['restricted']:
            restricted_nodes = self.add_polygon_to_graph(restricted)
            open_space_nodes['restricted'].append(restricted_nodes)
        return open_space_nodes

    def add_polygon_to_graph(self, polygon):
        self.current_node_id += 1
        origin = polygon.pop()
        self.add_osm_node(self.current_node_id, origin)
        nodes = [{'node_id': self.current_node_id, 'coord': origin}]
        self.current_node_id += 1
        for coord in polygon:
            self.add_osm_node(self.current_node_id, coord)
            self.add_osm_edge(nodes[-1]['node_id'], self.current_node_id)
            nodes.append({'node_id': self.current_node_id, 'coord': coord})
            self.current_node_id += 1
        self.add_osm_edge(nodes[-1]['node_id'], nodes[0]['node_id'])
        return nodes

    def add_entry_point_edges(self, nodes):
        for node in nodes:
            self.add_osm_edge(node['node_id'], node['entry_point_id'])

    def get_connection_points(self, open_space):
        entry_point_street_node_map = []
        for entry_point in open_space['entry_points']:
            print(entry_point)
            node = ox.get_nearest_node(self.graph, self.get_inverse_coord(entry_point))
            entry_point_street_node_map.append({'street_node_id': node, 'entry_coord': entry_point})
        return entry_point_street_node_map

    def add_entry_point_connection(self, entry_point_street_node_map):
        for point_obj in entry_point_street_node_map:
            node_id, dist = ox.get_nearest_node(self.graph, self.get_inverse_coord(point_obj['entry_coord']),
                                                return_dist=True)
            print(dist)
            self.add_osm_edge(node_id, point_obj['street_node_id'])

    def is_visible_edge(self, open_space, line):
        touch_bools = []
        for restriced_area in open_space['restricted']:
            prep_not_walkable_poly = prep(Polygon([[elem['coord'][0], elem['coord'][1]] for elem in restriced_area]))
            restriced_areas_without_current = open_space['restricted'].copy().remove(restriced_area)
            expression_not_intersect = not prep_not_walkable_poly.intersects(line)
            expression_touches = prep_not_walkable_poly.touches(line)
            if restriced_areas_without_current:
                # TODO: simplify
                expression_not_intersect_other = all(
                    [not self.get_prep_poly(restriced_area_intersectable).intersects(line) for
                     restriced_area_intersectable
                     in restriced_areas_without_current])
            else:
                expression_not_intersect_other = True
            expression = (expression_not_intersect or expression_touches) and expression_not_intersect_other
            touch_bools.append(expression)
        return all(touch_bools)

    def get_prep_poly(self, restriced_area_intersectable):
        return prep(Polygon([elem['coord']
                             for elem in restriced_area_intersectable]))

    def add_visiblity_graph_edges(self, open_space):
        added_edges = 0
        open_space_polygon_arr = [[elem['coord'][0], elem['coord'][1]] for elem in open_space['walkables'][0]]
        open_space_poly = Polygon(open_space_polygon_arr)
        prep_open_space_poly = prep(open_space_poly)
        nodes = self.get_all_nodes(open_space)

        for open_space_elem_from in nodes:
            for open_space_elem_to in nodes:
                if open_space_elem_from['node_id'] < open_space_elem_to['node_id']:
                    new_possible_edge = LineString([open_space_elem_from['coord'], open_space_elem_to['coord']])
                    if prep_open_space_poly.covers(new_possible_edge) and self.is_visible_edge(open_space,
                                                                                               new_possible_edge):
                        added_edges += 1
                        self.add_osm_edge(open_space_elem_from['node_id'], open_space_elem_to['node_id'])

        print(f'ADDED_EDGES:\t{added_edges}')

    def insert_open_space(self, open_space):
        entry_points_map = self.get_connection_points(open_space)
        open_space_nodes = self.add_open_space_to_graph(open_space)
        self.add_visiblity_graph_edges(open_space_nodes)
        self.add_entry_point_connection(entry_points_map)

    @staticmethod
    def get_inverse_coord(coord):
        return [coord[1], coord[0]]

    @staticmethod
    def get_all_nodes(open_space):
        nodes = []
        for elem in open_space['walkables']:
            nodes.extend(elem)
        for elem in open_space['restricted']:
            nodes.extend(elem)
        return nodes
