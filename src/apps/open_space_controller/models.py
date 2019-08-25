from typing import List

# Create your models here.
from apps.lector.models import EntryPoint


class BBox:
    def __init__(self, max_lat: float, min_lat: float, max_lon: float, min_lon: float):
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_lon = min_lon
        self.max_lon = max_lon

    def get_bbox(self) -> List[float]:
        return [self.max_lat, self.min_lat, self.max_lon, self.min_lon]


class OpenSpace:
    def __init__(self, file_name: str, walkable_area: List[List[float]], restricted_areas: List[List[List[float]]],
                 blocked_areas: List[List[List[float]]], entry_points: List[EntryPoint], buildings=None):
        self.file_name = file_name
        self.walkable_area_coords = walkable_area
        self.restricted_areas_coords = restricted_areas
        self.blocked_areas_coords = blocked_areas
        self.entry_points = entry_points
        self.buildings = buildings

    def is_contained_building(self, building) -> bool:
        bbox = self.get_boundaries(boundary_degree_extension=0.0005)
        for staircase in building.staircases:
            # TODO check bbox
            if bbox.max_lat >= staircase.coord[1] >= bbox.min_lat and bbox.max_lon >= staircase.coord[
                0] >= bbox.min_lon:
                return True
        return False

    def set_buildings(self, buildings):
        self.buildings = [building for building in buildings if self.is_contained_building(building)]

    def get_boundaries(self, boundary_degree_extension=0.0) -> BBox:
        longitudes, latitudes = zip(*self.walkable_area_coords)

        min_lat = min(latitudes) - boundary_degree_extension
        max_lat = max(latitudes) + boundary_degree_extension
        min_lon = min(longitudes) - boundary_degree_extension
        max_lon = max(longitudes) + boundary_degree_extension
        return BBox(max_lat, min_lat, max_lon, min_lon)

    def get_minimal_dict(self):
        buildings = []
        if self.buildings:
            buildings = self.buildings
        return {"file_name": self.file_name,
                "walkable_area_nodes": len(self.walkable_area_coords),
                "restricted_areas": len(self.restricted_areas_coords),
                "blocked_areas": len(self.blocked_areas_coords),
                "entry_points": len(self.entry_points),
                "buildings": len(buildings)
                }
