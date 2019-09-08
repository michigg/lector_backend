from __future__ import unicode_literals

import logging

from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.building_controller.config_controller import BuildingConfigController
from apps.open_space_controller.config_controller import OpenSpaceConfigController
from .serializer import MovementTypeSerializer, FileNameSerializer

logger = logging.getLogger(__name__)
'''
Author: Michael Götz
'''


@permission_classes((AllowAny,))
class ApiListOpenSpaces(views.APIView):
    def get(self, request):
        open_space_c = OpenSpaceConfigController()
        files = [{"file_name": f} for f in open_space_c.get_open_spaces_files()]
        files.sort(key=lambda x: x['file_name'])
        results = FileNameSerializer(files, many=True).data
        return Response(results, status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})


@permission_classes((AllowAny,))
class ApiListOpenSpaceGeoJson(views.APIView):
    def get(self, request, file_name):
        open_space_c = OpenSpaceConfigController()
        geojson = open_space_c.load_geojson(file_name)
        if geojson:
            return Response(geojson, status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
        return Response(status=status.HTTP_400_BAD_REQUEST, headers={'access-control-allow-origin': '*'})


@permission_classes((AllowAny,))
class ApiListOpenSpaceConfig(views.APIView):
    def get(self, request, file_name):
        open_space_cc = OpenSpaceConfigController()
        open_space = open_space_cc.get_open_space(file_name)
        if open_space:
            building_c = BuildingConfigController()
            open_space.set_buildings(building_c.buildings)
            return Response(open_space.get_minimal_dict(),
                            status=status.HTTP_200_OK,
                            headers={'access-control-allow-origin': '*'})
        return Response(status=status.HTTP_400_BAD_REQUEST, headers={'access-control-allow-origin': '*'})
