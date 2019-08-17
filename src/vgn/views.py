import json

import requests
from django.shortcuts import render

# Create your views here.
from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from vgn.utils.vgn_coord_models import VGNCoordConfigController, VGNCoordController

import logging

logger = logging.getLogger(__name__)


@permission_classes((AllowAny,))
class ApiVGNConnection(views.APIView):
    def get(self, request):
        from_lat = request.GET.get('from_lat', None)
        from_lon = request.GET.get('from_lon', None)
        building_key = request.GET.get('building_key', None)
        if from_lat and from_lon and building_key:
            vgn_c = VGNCoordController()
            vgn_coord = vgn_c.get_vgn_coord(building_key)
            response = requests.get(
                f"https://www.vgn.de/ib/site/tools/VN_PointLookup.php?class=coord&lon={from_lon}&lat={from_lat}")
            logger.debug(response.text)
            logger.debug(f"https://www.vgn.de/ib/site/tools/VN_PointLookup.php?class=coord&lon={from_lon}&lat={from_lat}")
            if vgn_coord and response.status_code == 200:
                to_coord = json.loads(response.text)['ident']['name']
                return Response(
                    {"url": f'https://www.vgn.de/verbindungen/?to=coord:{to_coord}&td={vgn_coord.vgn_url_segment}'},
                    status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
        return Response(status=status.HTTP_400_BAD_REQUEST, headers={'access-control-allow-origin': '*'})
