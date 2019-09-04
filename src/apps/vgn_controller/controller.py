import json
import logging
from typing import List

import requests

from apps.building_controller.controller import BuildingController
from apps.building_controller.models import Room

logger = logging.getLogger(__name__)
VGN_CONNECTIONS_URL = "https://www.vgn.de/verbindungen/"
VGN_POINT_LOOKUP_URL = "https://www.vgn.de/ib/site/tools/VN_PointLookup.php"


class VGNCoordController:
    def __init__(self):
        pass

    def get_vgn_connections_link(self, from_coord: str, to_coord: str):
        return f'{VGN_CONNECTIONS_URL}?to=coord:{from_coord}&td=coord:{to_coord}'

    def get_vgn_coord(self, lon: float, lat: float) -> str:
        response = requests.get(f"{VGN_POINT_LOOKUP_URL}?class=coord&lon={lon}&lat={lat}")
        return json.loads(response.text)['ident']['name'] if response.status_code == 200 else None
