import json

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.lector.models import EntryPoint
from apps.open_space_controller.config_controller import OpenSpaceConfigController
from apps.open_space_controller.models import OpenSpace

TEST_DIR = "/test/data/open_space_controller"


# Create your tests here.
class OpenSpaceControllerApiTest(TestCase):
    def load_json(self, file_name) -> dict:
        with open(f'{TEST_DIR}/api/{file_name}', 'r') as f:
            return json.load(f)

    def setUp(self) -> None:
        self.client = APIClient()

    def test_movement_types(self):
        url = reverse('movement-types')
        response = self.client.get(url, format='json')
        expected_data = self.load_json('')
        self.assertEqual(response.data, )


#
#     def test_with_empty_token(self):
#         response = self.client.get('/api/v1/univis/rooms/', {'token': ''}, format='json')
#         self.assertEqual(response.status_code, 400)
#
#     def test_without_token(self):
#         response = self.client.get('/api/v1/univis/rooms/', format='json')
#         self.assertEqual(response.status_code, 400)


class OpenSpaceConfigControllerTest(TestCase):
    def test_empty_config_file(self):
        config_controller = OpenSpaceConfigController(
            config_dir=f'{TEST_DIR}/config_controller/empty')
        self.assertEqual(len(config_controller.open_spaces), 0)

    def test_no_walkable_config_file(self):
        config_controller = OpenSpaceConfigController(
            config_dir=f'{TEST_DIR}/config_controller/no_walkable')
        self.assertEqual(len(config_controller.open_spaces), 0)

    def test_multiple_walkables_config_file(self):
        config_controller = OpenSpaceConfigController(
            config_dir=f'{TEST_DIR}/config_controller/multiple_walkable')
        self.assertEqual(len(config_controller.open_spaces), 0)

    def test_default_config_file(self):
        config_controller = OpenSpaceConfigController(
            config_dir=f'{TEST_DIR}/config_controller/default')
        self.assertEqual(len(config_controller.open_spaces), 2)

    def test_open_space_correct_loaded(self):
        entry_1 = EntryPoint([10.903171598911285, 49.907197803913526])
        entry_2 = EntryPoint([10.903244018554688, 49.90710452333503])
        expected_open_space = OpenSpace('feki.geojson',
                                        [
                                            [10.90245008468628, 49.908267062844295],
                                            [10.902847051620483, 49.90777821234866],
                                            [10.90245008468628, 49.908267062844295]
                                        ],
                                        [
                                            [
                                                [10.903726816177384, 49.90669339567286],
                                                [10.903995037078857, 49.906373819229145]
                                            ],
                                            [
                                                [10.905743837356567, 49.9067504009781],
                                                [10.90479701757431, 49.90643773468725],
                                                [10.905743837356567, 49.9067504009781]
                                            ],
                                        ],
                                        [
                                            [
                                                [10.904405415058136, 49.908685086546825],
                                                [10.90417206287384, 49.90864190244783],
                                                [10.904405415058136, 49.908685086546825]
                                            ],
                                            [
                                                [10.90440809726715, 49.90866954027564],
                                                [10.90440809726715, 49.90866954027564]
                                            ]
                                        ],
                                        [entry_1, entry_2]
                                        )
        config_controller = OpenSpaceConfigController(
            config_dir=f'{TEST_DIR}/config_controller/minimal')
        open_space = config_controller.get_open_space('feki.geojson')
        self.assertTrue(open_space)
        self.maxDiff = None
        self.assertEqual(open_space, expected_open_space)

    def test_open_space_coloring(self):
        config_controller = OpenSpaceConfigController(
            config_dir=f'{TEST_DIR}/config_controller/default')
        colored_geojson = config_controller.get_colored_geojson('feki_wrong_colored.geojson')

        with open(f'{TEST_DIR}/config_controller/default/feki.geojson', 'r') as f:
            expected_colored_geojson = json.load(f)
        self.maxDiff = None
        self.assertEqual(colored_geojson['geojson'], expected_colored_geojson)
