from __future__ import unicode_literals

import datetime
import json
import logging

from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.lector.serializer import FileNameSerializer
from .config_controller import BuildingConfigController
from .controller import BuildingController
from .models import Room

logger = logging.getLogger(__name__)
'''
Author: Michael Götz
'''


@permission_classes((AllowAny,))
class ApiBuildings(views.APIView):
    def get(self, request):
        request.GET.get('from_lat', None)
        building_c = BuildingConfigController()
        files = [{"file_name": f} for f in building_c.get_building_config_files()]
        files.sort(key=lambda x: x['file_name'])
        results = FileNameSerializer(files, many=True).data
        return Response(results, status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})


@permission_classes((AllowAny,))
class ApiBuilding(views.APIView):
    def get(self, request, file_name):
        building_c = BuildingConfigController()
        building_json = building_c.get_building_config(file_name)
        if building_json:
            return Response(building_json, status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
        return Response(status=status.HTTP_400_BAD_REQUEST, headers={'access-control-allow-origin': '*'})


@permission_classes((AllowAny,))
class ApiRoomCoord(views.APIView):
    def get(self, request, building, level, number):
        room_staircase_c = BuildingController()
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


@permission_classes((AllowAny,))
class ApiRoomBuilding(views.APIView):
    def get(self, request, building_key, level, number):
        room_staircase_c = BuildingController()
        building = room_staircase_c.get_rooms_building(Room(building_key, level, number))

        if building:
            building_json = json.loads(
                json.dumps(building.__dict__, default=lambda o: o.__dict__ if not isinstance(o, (datetime.date,
                                                                                                 datetime.datetime)) else o.isoformat(),
                           indent=4, cls=DjangoJSONEncoder))
            for staircase_json in building_json['staircases']:
                for entry in staircase_json['entries']:
                    entry['coord'] = entry['open_space_coord']
            return Response(building_json,
                            status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
        return Response(status=status.HTTP_400_BAD_REQUEST, headers={'access-control-allow-origin': '*'})
