import osmnx as ox

from lector.utils.docker_controller import DockerGraphhopperController
from lector.utils.open_space_config_controller import OpenSpaceConfigController
from lector.utils.open_space_controller import OpenSpaceController

ox.config(log_console=True, use_cache=True)

BAMBERG_BBOX = [49.865874134216426, 49.925145775384436, 10.836982727050781, 10.951995849609375]
# BAMBERG_BBOX = [49.9954, 49.7511, 10.7515, 11.1909]

OSM_OUTPUT_FILENAME = "data"
OSM_OUTPUT_DIR = "/osm_data"
SERVICE_NAME = 'graphhopper'
OPEN_SPACE_CONFIG_DIR = "/open_spaces"


class OSMManipulator:
    def __init__(self):
        self.gh_docker_controller = DockerGraphhopperController(graphhopper_service_name=SERVICE_NAME,
                                                                osm_output_dir=OSM_OUTPUT_DIR,
                                                                osm_output_filename=OSM_OUTPUT_FILENAME)
        self.osp_config_c = OpenSpaceConfigController(OPEN_SPACE_CONFIG_DIR)
        G = self.download_map()
        self.osp_c = OpenSpaceController(G)

    def insert_open_spaces(self):
        open_spaces = self.osp_config_c.get_open_spaces()
        for open_space in open_spaces:
            self.osp_c.insert_open_space(open_space)

    @staticmethod
    def download_map():
        return ox.graph_from_address('Markusplatz, Bamberg, Oberfranken, Bayern, 96047, Deutschland',
                                     network_type='all',
                                     distance=300)

    @staticmethod
    def load_map():
        return ox.graph_from_file(f'{OSM_OUTPUT_DIR}/{OSM_OUTPUT_FILENAME}.osm')

    @staticmethod
    def plot_graph(G):
        ox.plot_graph(G, save=True,
                      file_format='svg',
                      filename=f'{OSM_OUTPUT_DIR}/network_plot',
                      edge_linewidth=0.2,
                      node_size=2)

    @staticmethod
    def save_graph(G):
        ox.save_graph_osm(G, filename=f'{OSM_OUTPUT_FILENAME}.osm',
                          folder=OSM_OUTPUT_DIR)


if __name__ == '__main__':
    G = ox.graph_from_address('Markusplatz, Bamberg, Oberfranken, Bayern, 96047, Deutschland',
                              network_type='all',
                              distance=300)
    # pprint(G.edges.data())
    osmman = OSMManipulator()
    osmman.insert_open_spaces(G)
    osmman.gh_docker_controller.clean_graphhopper_restart()
    ox.add_edge_lengths(G)
    print(G.edges.data())

    print("GRAPH LOADED")
    osmman.plot_graph(G)
    print("GRAPH PLOTTED")
    osmman.save_graph(G)

    gh_controller = DockerGraphhopperController()
    gh_controller.clean_graphhopper_restart()
