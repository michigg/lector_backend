# Create your views here.

import logging

from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from building_controller.utils.building_models import Room
from building_controller.utils.indoor_mapper import RoomStaircaseController
from lecture_room_service.serializer import LonLatSerializer, RoomSerializer, \
    SplittedLectureSerializer
from lecture_room_service.utils.univis_lecture_controller import UnivISLectureController
from lecture_room_service.utils.univis_room_controller import UnivISRoomController

logger = logging.getLogger(__name__)


@permission_classes((AllowAny,))
class ApiLectures(views.APIView):
    def get(self, request):
        search_token = request.GET.get('token', None)
        if search_token:
            univis_lecture_c = UnivISLectureController()
            lectures = univis_lecture_c.get_lectures_by_token(search_token)
            if lectures:
                lectures_after, lectures_before = univis_lecture_c.get_lectures_split_by_date(lectures)
                lectures_dict = {'before': lectures_before, 'after': lectures_after}
                lectures_dict['before'] = self.get_lectures_as_dicts(lectures_dict['before'])
                lectures_dict['after'] = self.get_lectures_as_dicts(lectures_dict['after'])
                results = SplittedLectureSerializer(lectures_dict, many=False).data

                return Response(results, status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
            else:
                return Response(status=status.HTTP_204_NO_CONTENT, headers={'access-control-allow-origin': '*'})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, headers={'access-control-allow-origin': '*'})

    def get_lectures_as_dicts(self, lectures):
        return [lecture.__dict__ for lecture in lectures]


@permission_classes((AllowAny,))
class ApiRooms(views.APIView):
    def get(self, request):
        search_token = request.GET.get('token', None)
        if search_token:
            univis_room_c = UnivISRoomController()
            rooms = sorted(univis_room_c.get_rooms_by_token(token=search_token), key=lambda room: room.__str__())
            room_dicts = []
            for room in rooms:
                room_dicts.append(room.__dict__)
            results = RoomSerializer(room_dicts, many=True).data
            return Response(results, status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, headers={'access-control-allow-origin': '*'})


@permission_classes((AllowAny,))
class ApiRoomCoord(views.APIView):
    def get(self, request):
        building = request.GET.get('building', None)
        level = request.GET.get('level', None)
        number = request.GET.get('number', None)
        if building and level and number:
            room_staircase_c = RoomStaircaseController()
            staircase = room_staircase_c.get_rooms_staircase(Room(building, level, number))
            if staircase:
                result = LonLatSerializer({'longitude': staircase.coord[0], 'latitude': staircase.coord[1]},
                                          many=False).data
                return Response(result,
                                status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
        return Response(status=status.HTTP_400_BAD_REQUEST, headers={'access-control-allow-origin': '*'})
