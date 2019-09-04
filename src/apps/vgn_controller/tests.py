from django.test import TestCase
from rest_framework.test import APIClient


# Create your tests here.
class VGNControllerTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_with_coords_correct_url(self):
        response = self.client.get('/api/v1/vgn/',
                                   {'from_lon': 10.8911,
                                    'from_lat': 49.8934,
                                    'to_lon': 10.905089378356934,
                                    'to_lat': 49.90699828690093
                                    },
                                   format='json')
        self.assertEqual(response.data, {
            "url": "https://www.vgn.de/verbindungen/?to=coord:10.8911:49.8934:WGS84[DD.DDDDD]:Bamberg, Franz-Ludwig-Straße 8&td=coord:10.905089378356934:49.90699828690093:WGS84[DD.DDDDD]:Bamberg, Feldkirchenstraße 21"
        })

    def test_without_coords_400(self):
        response = self.client.get('/api/v1/vgn/', format='json')
        self.assertEqual(response.status_code, 400)
