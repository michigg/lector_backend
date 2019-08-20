from __future__ import unicode_literals

import datetime
import json
import os
import stat
from django.utils import timezone
from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from building_controller.utils.building_models import Room
from building_controller.utils.config_controller import IndoorMapperConfigController
from building_controller.utils.indoor_mapper import RoomStaircaseController
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
class ApiBuildings(views.APIView):
    def get(self, request):
        building_c = IndoorMapperConfigController()
        files = [{"file_name": f} for f in building_c.get_building_config_files()]
        files.sort(key=lambda x: x['file_name'])
        results = FileNameSerializer(files, many=True).data
        return Response(results, status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})


@permission_classes((AllowAny,))
class ApiBuilding(views.APIView):
    def get(self, request, file_name):
        building_c = IndoorMapperConfigController()
        building_json = building_c.load_building_config(file_name)
        if building_json:
            return Response(building_json, status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
        return Response(status=status.HTTP_400_BAD_REQUEST, headers={'access-control-allow-origin': '*'})


@permission_classes((AllowAny,))
class ApiRoomCoord(views.APIView):
    def get(self, request, building, level, number):
        room_staircase_c = RoomStaircaseController()
        staircase = room_staircase_c.get_rooms_staircase(Room(building, level, number))
        if staircase:
            staircase_json = json.loads(json.dumps(staircase.__dict__, default=lambda o: o.__dict__, indent=4))
            for entry in staircase_json['entries']:
                entry['coord'] = entry['open_space_coord']
            return Response(staircase_json,
                            status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
        return Response(status=status.HTTP_400_BAD_REQUEST, headers={'access-control-allow-origin': '*'})

# @permission_classes((AllowAny,))
# class ApBuildingInfos(views.APIView):
#     def get(self, request):
#         file_name = request.GET.get('file_name', None)
#         if file_name:
#             osmm = OSMManipulator()
#             building_c = IndoorMapperConfigController()
#             # open_space = building_(file_name)
#             try:
#                 timestamp = os.path.getctime(f'{settings.MEDIA_ROOT}/{open_space.file_name}.svg')
#                 creation_time = datetime.datetime.fromtimestamp(timestamp, tz=timezone.get_current_timezone())
#                 max_creation_time = timezone.localtime(timezone.now()) - datetime.timedelta(
#                     hours=settings.OPEN_SPACE_MAX_CACHING_TIME)
#
#                 if creation_time < max_creation_time:
#                     osmm.create_open_space_plot(open_space, settings.MEDIA_ROOT)
#             except FileNotFoundError as err:
#                 osmm.create_open_space_plot(open_space, settings.MEDIA_ROOT)
#
#             return Response({"url": f'{settings.MEDIA_URL}{open_space.file_name}.svg'},
#                             status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
#         else:
#             return Response(status=status.HTTP_400_BAD_REQUEST, headers={'access-control-allow-origin': '*'})
