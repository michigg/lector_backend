import json
import tempfile

from django.test import TestCase, override_settings

# Create your tests here.
from django.urls import reverse
from rest_framework.test import APIClient

from apps.lector.controllers import OSMController

PLOT_OUTPUT_DIR = "/test/plots"
OPEN_SPACE_FILE_NAME = "markusplatz.geojson"
BLOCKED_OPEN_SPACE_FILE_NAME = "markusplatz_blocked.geojson"
TEST_DIR = "/test/data/lector"


class LectorApiTest(TestCase):
    def load_json(self, file_name) -> dict:
        with open(f'{TEST_DIR}/api/{file_name}', 'r') as f:
            return json.load(f)

    def setUp(self) -> None:
        self.client = APIClient()

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_api_open_space_plot(self):
        url = reverse('open-space-plot', kwargs={'file_name': 'erba.geojson'})
        response = self.client.get(url, format='json')
        expected_data = self.load_json(f'plot_url_result.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected_data)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_api_open_space_plot_cache(self):
        url = reverse('open-space-plot', kwargs={'file_name': 'erba.geojson'})
        self.client.get(url, format='json')
        response = self.client.get(url, format='json')
        expected_data = self.load_json(f'plot_url_result.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected_data)

    def test_api_open_space_plot_with_wrong_filename(self):
        url = reverse('open-space-plot', kwargs={'file_name': 'missing.geojson'})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 400)


class GraphTests(TestCase):
    def setUp(self):
        self.osmm = OSMController(open_space_config_dir="/test/data/open_spaces",
                                  building_config_dir="/test/data/buildings/unblocked")

    def test_open_space_entries(self):
        open_space = self.osmm.osp_config_c.get_open_space(OPEN_SPACE_FILE_NAME)
        self.osmm.create_open_space_entries_plot(open_space,
                                                 output_dir=f'{PLOT_OUTPUT_DIR}',
                                                 file_name=f'00_-_test_open_space_entries_-_{open_space.file_name}')

    def test_open_space_walkable(self):
        open_space = self.osmm.osp_config_c.get_open_space(OPEN_SPACE_FILE_NAME)
        self.osmm.create_open_space_walkable_plot(open_space,
                                                  output_dir=f'{PLOT_OUTPUT_DIR}',
                                                  file_name=f'01_-_test_open_space_walkable_-_{open_space.file_name}')

    def test_open_space_restricted_areas(self):
        open_space = self.osmm.osp_config_c.get_open_space(OPEN_SPACE_FILE_NAME)
        self.osmm.create_open_space_restricted_plot(open_space,
                                                    output_dir=f'{PLOT_OUTPUT_DIR}',
                                                    file_name=f'02_-_test_open_space_restricted_areas_-_{open_space.file_name}')

    def test_open_space_walkable_and_restricted(self):
        open_space = self.osmm.osp_config_c.get_open_space(OPEN_SPACE_FILE_NAME)
        self.osmm.create_open_space_walkable_restricted_plot(open_space,
                                                             output_dir=f'{PLOT_OUTPUT_DIR}',
                                                             file_name=f'03_-_test_open_space_walkable_and_restricted_-_{open_space.file_name}')

    def test_open_space_walkable_and_restricted_and_entries(self):
        open_space = self.osmm.osp_config_c.get_open_space(OPEN_SPACE_FILE_NAME)
        self.osmm.create_open_space_walkable_restricted_entries_plot(open_space,
                                                                     output_dir=f'{PLOT_OUTPUT_DIR}',
                                                                     file_name=f'04_-_test_open_space_walkable_and_restricted_and_entries_-_{open_space.file_name}')

    def test_open_space_visibility_graph(self):
        open_space = self.osmm.osp_config_c.get_open_space(OPEN_SPACE_FILE_NAME)
        self.osmm.create_open_space_visibility_graph_plot(open_space,
                                                          output_dir=f'{PLOT_OUTPUT_DIR}',
                                                          file_name=f'05_-_test_open_space_visibility_graph_-_{open_space.file_name}')

    def test_blocked_open_space_visibility_graph(self):
        open_space = self.osmm.osp_config_c.get_open_space(BLOCKED_OPEN_SPACE_FILE_NAME)
        self.osmm.create_open_space_visibility_graph_plot(open_space,
                                                          output_dir=f'{PLOT_OUTPUT_DIR}',
                                                          file_name=f'B_05_-_test_open_space_visibility_graph_-_{open_space.file_name}')

    def test_open_space(self):
        open_space = self.osmm.osp_config_c.get_open_space(OPEN_SPACE_FILE_NAME)
        self.osmm.create_complete_open_space_plot(open_space,
                                                  output_dir=f'{PLOT_OUTPUT_DIR}',
                                                  file_name=f'06_-_test_open_space_-_{open_space.file_name}')

    def test_blocked_open_space(self):
        open_space = self.osmm.osp_config_c.get_open_space(BLOCKED_OPEN_SPACE_FILE_NAME)
        self.osmm.create_complete_open_space_plot(open_space,
                                                  output_dir=f'{PLOT_OUTPUT_DIR}',
                                                  file_name=f'B_06_-_test_open_space_-_{open_space.file_name}')

    def test_open_space_buildings(self):
        buildings = self.osmm.indoor_map_c.building_cc.get_buildings()
        open_space = self.osmm.osp_config_c.get_open_space(OPEN_SPACE_FILE_NAME)
        self.osmm.create_open_space_buildings_plot(open_space, buildings,
                                                   output_dir=f'{PLOT_OUTPUT_DIR}',
                                                   file_name=f'07_-_test_open_space_buildings_-_{open_space.file_name}')

    def test_open_space_buildings_blocked_staircase_and_entries(self):
        osmm = OSMController(open_space_config_dir="/test/data/open_spaces",
                             building_config_dir="/test/data/buildings/blocked")
        buildings = osmm.indoor_map_c.building_cc.get_buildings()
        open_space = osmm.osp_config_c.get_open_space(OPEN_SPACE_FILE_NAME)
        osmm.create_open_space_buildings_plot(open_space, buildings,
                                              output_dir=f'{PLOT_OUTPUT_DIR}',
                                              file_name=f'B_07_-_test_open_space_buildings_blocked_staircase_and_entries_-_{open_space.file_name}')
