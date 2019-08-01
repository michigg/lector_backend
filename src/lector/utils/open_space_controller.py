import logging

from lector.utils.open_space_config_controller import OpenSpaceConfigController
from lector.utils.open_space_models import OpenSpace
from lector.utils.graph_open_space_models import GraphOpenSpace
from lector.utils.osmm import OSMManipulator

logger = logging.getLogger(__name__)

OPEN_SPACE_CONFIG_DIR = "/open_spaces"


class OpenSpaceController:
    def __init__(self, osmm: OSMManipulator):
        self.osmm = osmm
        self.osp_config_c = OpenSpaceConfigController(OPEN_SPACE_CONFIG_DIR)
        self.inserted_open_spaces = []

    def insert_open_spaces(self):
        open_spaces = self.osp_config_c.get_open_spaces()
        for open_space in open_spaces:
            self.insert_open_space(open_space)

    def insert_open_space(self, open_space: OpenSpace):
        logger.info(f'Insert Open Space')
        logger.info(f'Graph Nodes: {len(self.osmm.graph)}')
        graph_open_space = GraphOpenSpace(open_space, self.osmm)
        graph_open_space.add_visiblity_graph_edges()
        graph_open_space.add_entry_edges()
        # graph_open_space.add_walkable_edges()
        # graph_open_space.add_restricted_area_edges()
        self.osmm.current_osm_id = graph_open_space.current_osm_id
        self.inserted_open_spaces.append(graph_open_space)
        logger.info(f'Graph Nodes: {len(self.osmm.graph)}')
