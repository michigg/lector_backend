from typing import List


# Create your models here.
class VGNCoord:
    def __init__(self, location: str, coord: List[float], vgn_url_segment: str, building_key: str):
        self.location = location
        self.coord = coord
        self.vgn_url_segment = vgn_url_segment
        self.building_key = building_key

    def is_coord(self, building_key: str):
        return building_key.lower() == self.building_key.lower()
