from .config_controller import VGNCoordConfigController
from .models import VGNCoord


class VGNCoordController:
    def __init__(self):
        self.config = VGNCoordConfigController()

    def get_vgn_coord(self, building_key) -> VGNCoord or None:
        for vgn_coord in self.config.vgn_coords:
            if vgn_coord.is_coord(building_key):
                return vgn_coord
        return None
