# Create your views here.

import logging

from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .controllers import UnivISRoomController, UnivISLectureController
from .serializer import RoomSerializer, SplittedLectureSerializer

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
            rooms = sorted(univis_room_c.get_tokens_rooms(token=search_token), key=lambda room: room.__str__())
            room_dicts = []
            for room in rooms:
                room_dicts.append(room.__dict__)
            results = RoomSerializer(room_dicts, many=True).data
            return Response(results, status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, headers={'access-control-allow-origin': '*'})
