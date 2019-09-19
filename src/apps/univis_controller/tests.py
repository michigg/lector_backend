import json

from django.test import TestCase
from rest_framework.test import APIClient
from django.conf import settings

TEST_DATA_DIR = "/test/data/univis_controller"


# Create your tests here.
class UnivisControllerRoomsApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_with_token(self):
        response = self.client.get('/api/v1/univis/rooms/',
                                   {'token': 'f21'},
                                   format='json')
        with open(f'{TEST_DATA_DIR}/f21_rooms.json', 'r') as f:
            expected_rooms_json = json.load(f)
        self.assertEqual(response.status_code, 200)
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
        with open(f'{TEST_DATA_DIR}/mobass_lectures.json', 'r') as f:
            expected_lectures_json = json.load(f)
        self.assertEqual(response.status_code, 200)
        response_data = str(json.loads(response.content))
        self.assertTrue(response_data.find(str(expected_lectures_json['before'][0])) > -1)
        self.assertTrue(response_data.find(str(expected_lectures_json['before'][1])) > -1)
        self.assertTrue(response_data.find("before") > -1)
        self.assertTrue(response_data.find("after") > -1)

    def test_with_token_results_in_no_content(self):
        response = self.client.get('/api/v1/univis/lectures/', {'token': 'asdf'}, format='json')
        self.assertEqual(response.status_code, 204)

    def test_with_empty_token(self):
        response = self.client.get('/api/v1/univis/lectures/', {'token': ''}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_without_token(self):
        response = self.client.get('/api/v1/univis/lectures/', format='json')
        self.assertEqual(response.status_code, 400)
