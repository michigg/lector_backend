from __future__ import unicode_literals

import datetime
import json
import os
import stat

from django.core.serializers.json import DjangoJSONEncoder
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
            staircase_json = json.loads(
                json.dumps(staircase.__dict__, default=lambda o: o.__dict__ if not isinstance(o, (datetime.date,
                                                                                                  datetime.datetime)) else o.isoformat(),
                           indent=4, cls=DjangoJSONEncoder))
            for entry in staircase_json['entries']:
                entry['coord'] = entry['open_space_coord']
            return Response(staircase_json,
                            status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
        return Response(status=status.HTTP_400_BAD_REQUEST, headers={'access-control-allow-origin': '*'})
