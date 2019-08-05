# Create your views here.
from datetime import datetime

from django.utils import timezone
from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from indoor_mapper.utils.indoor_mapper import RoomStaircaseController
from indoor_mapper.utils.univis_models import MinimalRoom
from lecture_room_service.serializer import LectureSerializer, LonLatSerializer
from lecture_room_service.utils.univis_lecture_room_controller import UnivISLectureController

import logging

logger = logging.getLogger(__name__)


@permission_classes((AllowAny,))
class ApiLectures(views.APIView):
    def get(self, request):
        search_token = request.GET.get('token', None)
        if search_token:
            univis_lecture_c = UnivISLectureController()
            lectures = univis_lecture_c.get_lectures_by_token(search_token)
            lectures = sorted(lectures, key=lambda lecture: lecture.get_first_term().starttime)
            lectures_before = []
            lectures_after = []
            current_time = timezone.localtime(timezone.now())
            for lecture in lectures:
                logger.warn(current_time.time())
                logger.warn(lecture.get_last_term().starttime.time())
                logger.warn(lecture.get_last_term().starttime.time() < current_time.time())
                if lecture.get_last_term().starttime.time() < current_time.time():
                    lectures_before.append(lecture)
                else:
                    lectures_after.append(lecture)
            lectures = lectures_after
            lectures.extend(lectures_before)
            lectures_dicts = []
            for lecture in lectures:
                lectures_dicts.append(lecture.__dict__)
            results = LectureSerializer(lectures_dicts, many=True).data
            return Response(results, status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@permission_classes((AllowAny,))
class ApiRoomCoord(views.APIView):
    def get(self, request):
        building = request.GET.get('building', None)
        level = request.GET.get('level', None)
        number = request.GET.get('number', None)
        if building and level and number:
            room_staircase_c = RoomStaircaseController()
            staircase = room_staircase_c.get_rooms_staircase(MinimalRoom(building, level, number))
            if staircase:
                result = LonLatSerializer({'longitude': staircase.coord[0], 'latitude': staircase.coord[1]},
                                          many=False).data
                return Response(result,
                                status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
        return Response(status=status.HTTP_400_BAD_REQUEST)
