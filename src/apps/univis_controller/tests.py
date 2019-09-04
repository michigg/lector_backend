import json

from django.test import TestCase
from rest_framework.test import APIClient
from django.conf import settings

PLOT_OUTPUT_DIR = "/test/results/univis_controller"


# Create your tests here.
class UnivisControllerRoomsApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_with_token(self):
        response = self.client.get('/api/v1/univis/rooms/',
                                   {'token': 'f21'},
                                   format='json')
        with open(f'{PLOT_OUTPUT_DIR}/f21_rooms.json', 'r') as f:
            expected_rooms_json = json.load(f)
        self.assertEqual(response.data, expected_rooms_json)

    def test_with_empty_token(self):
        response = self.client.get('/api/v1/univis/rooms/', {'token': ''}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_without_token(self):
        response = self.client.get('/api/v1/univis/rooms/', format='json')
        self.assertEqual(response.status_code, 400)


class UnivisControllerLecturesApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_with_token(self):
        response = self.client.get('/api/v1/univis/lectures/',
                                   {'token': 'mobass'},
                                   format='json')
        with open(f'{PLOT_OUTPUT_DIR}/mobass_lectures.json', 'r') as f:
            expected_lectures_json = json.load(f)
        self.assertEqual(response.data, expected_lectures_json)

    def test_with_token_results_in_no_content(self):
        response = self.client.get('/api/v1/univis/lectures/', {'token': 'asdf'}, format='json')
        self.assertEqual(response.status_code, 204)

    def test_with_empty_token(self):
        response = self.client.get('/api/v1/univis/lectures/', {'token': ''}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_without_token(self):
        response = self.client.get('/api/v1/univis/lectures/', format='json')
        self.assertEqual(response.status_code, 400)
