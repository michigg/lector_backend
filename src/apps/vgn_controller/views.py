import json
import logging
from typing import List

import requests
# Create your views here.
from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .controller import VGNCoordController

logger = logging.getLogger(__name__)


@permission_classes((AllowAny,))
class ApiVGNConnection(views.APIView):
    def get(self, request):
        from_lat = request.GET.get('from_lat', None)
        from_lon = request.GET.get('from_lon', None)
        building_key = request.GET.get('building_key', None)
        level = request.GET.get('level', None)
        number = request.GET.get('number', None)

        if from_lat and from_lon and building_key and level and number:
            vgn_c = VGNCoordController()
            staircase_coord = vgn_c.get_rooms_staircase_coord(building_key, level, number)

            from_coord = vgn_c.get_vgn_coord(from_lon, from_lat)
            to_coord = vgn_c.get_vgn_coord(staircase_coord[0], staircase_coord[1])

            if from_coord and to_coord:
                return Response(
                    {"url": vgn_c.get_vgn_connections_link(from_coord, to_coord)},
                    status=status.HTTP_200_OK,
                    headers={'access-control-allow-origin': '*'})
        return Response(status=status.HTTP_400_BAD_REQUEST, headers={'access-control-allow-origin': '*'})
