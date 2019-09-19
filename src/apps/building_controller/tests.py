import json

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .test_data import expected_building_no_props, expected_building_wheelchair, expected_building_blocked_staircase, \
    expected_building_blocked_entries

# Create your tests here.
from apps.building_controller.config_controller import BuildingConfigController
from apps.building_controller.models import Building, StairCase, Floor, BuildingEntryPoint

TEST_DIR = "/test/data/building_controller"


class BuildingControllerApiTest(TestCase):
    def load_json(self, file_name) -> dict:
        with open(f'{TEST_DIR}/api/{file_name}', 'r') as f:
            return json.load(f)

    def setUp(self) -> None:
        self.client = APIClient()

    def test_api_buildings(self):
        url = reverse('buildings')
        response = self.client.get(url, format='json')
        expected_data = self.load_json(f'buildings_result.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected_data)

    def test_api_building_config(self):
        url = reverse('building', kwargs={'file_name': 'M3.json'})
        response = self.client.get(url, format='json')
        expected_data = self.load_json(f'building_config_result.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected_data)

    def test_building_config_with_wrong_filename(self):
        url = reverse('building', kwargs={'file_name': 'missing.json'})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 400)

    def test_api_rooms_building(self):
        url = reverse('room-building', kwargs={'building_key': 'M3', 'level': 1, 'number': 11})
        response = self.client.get(url, format='json')
        expected_data = self.load_json(f'room_building_result.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected_data)

    def test_api_rooms_building_with_wrong_building_key(self):
        url = reverse('room-building', kwargs={'building_key': 'M4', 'level': 1, 'number': 324})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 400)

    def test_api_rooms_staircase(self):
        url = reverse('staircase-room', kwargs={'building_key': 'M3', 'level': 1, 'number': 11})
        response = self.client.get(url, format='json')
        expected_data = self.load_json(f'room_staircase_result.json')
        print(json.loads(response.content))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected_data)

    def test_api_rooms_staircas_with_wrong_building_key(self):
        url = reverse('staircase-room', kwargs={'building_key': 'M4', 'level': 1, 'number': 324})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 400)


class BuildingConfigControllerTest(TestCase):
    def test_empty_config_file(self):
        config_controller = BuildingConfigController(
            config_dir=f'{TEST_DIR}/config_controller/empty')
        self.assertEqual(len(config_controller.get_buildings()), 0)

    def test_building_config_no_props(self):
        config_controller = BuildingConfigController(
            config_dir=f'{TEST_DIR}/config_controller/without_props')
        building = config_controller.get_buildings()[0]
        self.assertEqual(building, expected_building_no_props)

    def test_building_config_with_wheelchair(self):
        config_controller = BuildingConfigController(
            config_dir=f'{TEST_DIR}/config_controller/wheelchair')
        building = config_controller.get_buildings()[0]
        self.assertEqual(building, expected_building_wheelchair)

    def test_building_config_with_blocked_staircase(self):
        config_controller = BuildingConfigController(
            config_dir=f'{TEST_DIR}/config_controller/blocked_staircase')
        building = config_controller.get_buildings()[0]
        self.assertEqual(building, expected_building_blocked_staircase)

    def test_building_config_with_blocked_entries(self):
        config_controller = BuildingConfigController(
            config_dir=f'{TEST_DIR}/config_controller/blocked_entry')
        building = config_controller.get_buildings()[0]
        self.assertEqual(building, expected_building_blocked_entries)
