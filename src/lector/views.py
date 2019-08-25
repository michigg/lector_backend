from __future__ import unicode_literals

import datetime
import os
from django.utils import timezone
from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from building_controller.config_controller import BuildingConfigController
from lector.serializer import MovementTypeSerializer, FileNameSerializer
from lector.utils.open_space_config_controller import OpenSpaceConfigController
from lector.utils.osmm import OSMManipulator
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
'''
Author: Michael Götz
'''


@permission_classes((AllowAny,))
class ApiListMovementTypes(views.APIView):
    def get(self, request):
        results = MovementTypeSerializer([{'id': '0', 'name': 'Pedestrian'}, {'id': '1', 'name': 'Bicycle'}],
                                         many=True).data
        return Response(results, status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})


@permission_classes((AllowAny,))
class ApiListOpenSpaces(views.APIView):
    def get(self, request):
        open_space_c = OpenSpaceConfigController()
        file_name = request.GET.get('file_name', None)
        if file_name:
            geojson = open_space_c.load_geojson(file_name)
            return Response(geojson, status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
        else:
            files = [{"file_name": f} for f in open_space_c.get_open_spaces_files()]
            files.sort(key=lambda x: x['file_name'])
            results = FileNameSerializer(files, many=True).data
            return Response(results, status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})


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
        open_space_c = OpenSpaceConfigController()
        open_space_c = open_space_c.get_open_space(file_name)
        building_c = BuildingConfigController()
        open_space_c.set_buildings(building_c.buildings)
        if open_space_c:
            logger.warn(open_space_c.__dict__)
            return Response(open_space_c.get_minimal_dict(), status=status.HTTP_200_OK,
                            headers={'access-control-allow-origin': '*'})
        return Response(status=status.HTTP_400_BAD_REQUEST, headers={'access-control-allow-origin': '*'})


@permission_classes((AllowAny,))
class ApiOpenSpacePlot(views.APIView):
    def get(self, request, file_name):
        osmm = OSMManipulator()
        open_space = osmm.osp_config_c.get_open_space(file_name)
        try:
            timestamp = os.path.getctime(f'{settings.MEDIA_ROOT}/{open_space.file_name}.svg')
            creation_time = datetime.datetime.fromtimestamp(timestamp, tz=timezone.get_current_timezone())
            max_creation_time = timezone.localtime(timezone.now()) - datetime.timedelta(
                hours=settings.OPEN_SPACE_MAX_CACHING_TIME)

            if creation_time < max_creation_time:
                osmm.create_open_space_plot(open_space, settings.MEDIA_ROOT)
        except FileNotFoundError as err:
            osmm.create_open_space_plot(open_space, settings.MEDIA_ROOT)

        return Response({"url": f'{settings.MEDIA_URL}{open_space.file_name}.svg'},
                        status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
